use aiken/collection/list
use aiken/crypto.{VerificationKeyHash}
use cardano/transaction.{OutputReference, Transaction}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/// On-chain record of an MPC initiation request.
/// The relay script polls for UTxOs containing this datum to bridge
/// Cardano (Layer 1) to Partisia Blockchain (Layer 2).
pub type MpcRequest {
  /// Identifies which Profila dataset to query
  dataset_id: ByteArray,
  /// The computation to run: "age_threshold" or "survey_match"
  query_type: ByteArray,
  /// Payment key hash of the requester — must match a tx signer
  initiator_pkh: VerificationKeyHash,
  /// Target Partisia contract address (may be empty at init)
  partisia_contract: ByteArray,
  /// POSIX timestamp in milliseconds when request was created
  timestamp: Int,
}

/// Redeemer actions for the Profila MPC contract.
pub type MpcAction {
  /// Record an MPC initiation intent on-chain
  InitiateMPC
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// Allowed query types as ByteArray literals
const query_age_threshold: ByteArray = "age_threshold"

const query_survey_match: ByteArray = "survey_match"

/// Seven days in milliseconds (7 * 24 * 60 * 60 * 1000)
const seven_days_ms: Int = 604_800_000

// ---------------------------------------------------------------------------
// Validator
// ---------------------------------------------------------------------------

validator profila_mpc {
  spend(
    datum: Option<MpcRequest>,
    redeemer: MpcAction,
    _utxo: OutputReference,
    self: Transaction,
  ) {
    // Datum must be present
    expect Some(request) = datum

    when redeemer is {
      InitiateMPC -> validate_initiate_mpc(request, self)
    }
  }

  else(_) {
    fail
  }
}

// ---------------------------------------------------------------------------
// Validation Logic
// ---------------------------------------------------------------------------

/// Validates an MPC initiation request against the transaction context.
///
/// Checks:
/// 1. The initiator must have signed the transaction
/// 2. The dataset_id must not be empty
/// 3. The query_type must be a recognised value
/// 4. The timestamp must be positive (basic sanity check)
fn validate_initiate_mpc(request: MpcRequest, tx: Transaction) -> Bool {
  let initiator_signed =
    list.has(tx.extra_signatories, request.initiator_pkh)

  let dataset_not_empty = request.dataset_id != ""

  let valid_query_type =
    request.query_type == query_age_threshold || request.query_type == query_survey_match

  let timestamp_positive = request.timestamp > 0

  // All conditions must pass — trace operator (?) logs which failed
  initiator_signed? && dataset_not_empty? && valid_query_type? && timestamp_positive?
}

// ---------------------------------------------------------------------------
// Utility (exported for use by tests and off-chain code)
// ---------------------------------------------------------------------------

/// Check whether a given query_type ByteArray is one of the allowed values.
pub fn is_valid_query_type(query_type: ByteArray) -> Bool {
  query_type == query_age_threshold || query_type == query_survey_match
}
