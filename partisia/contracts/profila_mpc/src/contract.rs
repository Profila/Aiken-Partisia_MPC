#[macro_use]
extern crate pbc_contract_codegen;
extern crate pbc_contract_common;
mod zk_compute;

use pbc_contract_common::address::Address;
use pbc_contract_common::context::ContractContext;
use pbc_contract_common::events::EventGroup;
use pbc_contract_common::zk::{
    CalculationStatus, SecretVarId, ZkClosed, ZkInputDef, ZkState, ZkStateChange,
};
use pbc_zk::Sbi64;

// ---------------------------------------------------------------------------
// Secret Variable Metadata
// ---------------------------------------------------------------------------

/// Tags each secret variable with its kind so the ZK computation
/// can filter and process them correctly.
#[derive(ReadWriteState, ReadWriteRPC, Debug)]
#[repr(u8)]
enum SecretVarType {
    /// A user-submitted secret value (age or survey answer)
    #[discriminant(0)]
    UserValue {},
    /// The computation result (count or sum)
    #[discriminant(1)]
    ComputeResult {},
}

// ---------------------------------------------------------------------------
// Contract State
// ---------------------------------------------------------------------------

/// Public on-chain state of the Profila MPC contract.
/// Individual secret values are NEVER stored here.
#[state]
struct ProfilaMpcState {
    /// Who deployed / administrates this contract
    administrator: Address,
    /// Identifies the Profila dataset being queried
    dataset_id: Vec<u8>,
    /// "age_threshold" or "survey_match"
    query_type: String,
    /// Minimum secrets required before computation can trigger
    min_participants: u32,
    /// The aggregate result after MPC computation completes
    result: Option<i64>,
    /// Whether the computation has finished
    computation_complete: bool,
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

/// Deploy the contract with dataset parameters.
/// Called once when the contract is first created on PBC testnet.
#[init(zk = true)]
fn initialize(
    ctx: ContractContext,
    _zk_state: ZkState<SecretVarType>,
    dataset_id: Vec<u8>,
    query_type: String,
    min_participants: u32,
) -> ProfilaMpcState {
    assert!(
        query_type == "age_threshold" || query_type == "survey_match",
        "query_type must be 'age_threshold' or 'survey_match'"
    );
    assert!(
        min_participants >= 2,
        "min_participants must be at least 2 for meaningful MPC"
    );

    ProfilaMpcState {
        administrator: ctx.sender,
        dataset_id,
        query_type,
        min_participants,
        result: None,
        computation_complete: false,
    }
}

// ---------------------------------------------------------------------------
// Secret Input Handler
// ---------------------------------------------------------------------------

/// Called when a Profila user submits their secret value.
///
/// For "age_threshold": the secret is the user's age (Sbi64).
/// For "survey_match":  the secret is 0 or 1 (Sbi64).
///
/// Each address can only submit once. The actual value is NEVER
/// visible in the public state — it goes directly into MPC secret sharing.
#[zk_on_secret_input(shortname = 0x40)]
fn submit_secret_value(
    context: ContractContext,
    state: ProfilaMpcState,
    zk_state: ZkState<SecretVarType>,
) -> (
    ProfilaMpcState,
    Vec<EventGroup>,
    ZkInputDef<SecretVarType, Sbi64>,
) {
    // Prevent duplicate submissions from the same address
    assert!(
        zk_state
            .secret_variables
            .iter()
            .chain(zk_state.pending_inputs.iter())
            .all(|(_, v)| v.owner != context.sender),
        "Each participant can only submit one secret value"
    );

    // Reject new inputs after computation is done
    assert!(
        !state.computation_complete,
        "Computation already complete — no more inputs accepted"
    );

    let input_def = ZkInputDef::with_metadata(
        Some(on_variable_inputted::SHORTNAME),
        SecretVarType::UserValue {},
    );

    (state, vec![], input_def)
}

/// Optional callback when a secret variable is confirmed on-chain.
/// We don't need to do anything here for the PoC, but it's good
/// practice to include the handler.
#[zk_on_variable_inputted(shortname = 0x41)]
fn on_variable_inputted(
    _context: ContractContext,
    state: ProfilaMpcState,
    _zk_state: ZkState<SecretVarType>,
    _inputted_variable: SecretVarId,
) -> ProfilaMpcState {
    state
}

// ---------------------------------------------------------------------------
// Trigger Computation
// ---------------------------------------------------------------------------

/// Public action to start the MPC computation.
/// Only the administrator can trigger this, and only when enough
/// participants have submitted their secrets.
#[action(shortname = 0x01, zk = true)]
fn start_computation(
    context: ContractContext,
    state: ProfilaMpcState,
    zk_state: ZkState<SecretVarType>,
) -> (ProfilaMpcState, Vec<EventGroup>, Vec<ZkStateChange>) {
    assert_eq!(
        context.sender, state.administrator,
        "Only the administrator can trigger computation"
    );
    assert_eq!(
        zk_state.calculation_state,
        CalculationStatus::Waiting,
        "Computation already in progress or complete"
    );

    let participant_count = zk_state.secret_variables.len() as u32;
    assert!(
        participant_count >= state.min_participants,
        "Not enough participants: have {}, need {}",
        participant_count,
        state.min_participants
    );

    // Start the ZK computation defined in zk_compute.rs
    (
        state,
        vec![],
        vec![zk_compute::compute_result::start(
            Some(on_compute_complete::SHORTNAME),
            &SecretVarType::ComputeResult {},
        )],
    )
}

// ---------------------------------------------------------------------------
// Computation Complete Callback
// ---------------------------------------------------------------------------

/// Called automatically when the MPC computation finishes.
/// Requests declassification of the aggregate result.
#[zk_on_compute_complete(shortname = 0x42)]
fn on_compute_complete(
    _context: ContractContext,
    state: ProfilaMpcState,
    _zk_state: ZkState<SecretVarType>,
    output_variables: Vec<SecretVarId>,
) -> (ProfilaMpcState, Vec<EventGroup>, Vec<ZkStateChange>) {
    // Open (declassify) the result variable so we can read it
    (
        state,
        vec![],
        vec![ZkStateChange::OpenVariables {
            variables: output_variables,
        }],
    )
}

// ---------------------------------------------------------------------------
// Variables Opened Callback
// ---------------------------------------------------------------------------

/// Called after the result variable is declassified.
/// Reads the aggregate value and stores it in public state.
#[zk_on_variables_opened]
fn on_variables_opened(
    _context: ContractContext,
    mut state: ProfilaMpcState,
    zk_state: ZkState<SecretVarType>,
    opened_variables: Vec<SecretVarId>,
) -> (ProfilaMpcState, Vec<EventGroup>, Vec<ZkStateChange>) {
    let opened_var = zk_state
        .get_variable(*opened_variables.first().expect("No opened variables"))
        .expect("Variable not found in ZK state");

    if let SecretVarType::ComputeResult {} = opened_var.metadata {
        let result_value = read_variable_i64_le(&opened_var);
        state.result = Some(result_value);
        state.computation_complete = true;

        return (state, vec![], vec![ZkStateChange::ContractDone]);
    }

    (state, vec![], vec![])
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Read a declassified variable's data as a little-endian i64.
fn read_variable_i64_le(var: &ZkClosed<SecretVarType>) -> i64 {
    let data = var.data.as_ref().expect("Variable has no data");
    let mut buffer = [0u8; 8];
    let len = data.len().min(8);
    buffer[..len].copy_from_slice(&data[..len]);
    i64::from_le_bytes(buffer)
}
