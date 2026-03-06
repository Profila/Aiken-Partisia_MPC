use pbc_zk::*;

/// Metadata discriminant for user-submitted secret values.
/// Must match SecretVarType::UserValue discriminant (0) in contract.rs.
const USER_VALUE_KIND: u8 = 0u8;

/// The age threshold for the "age_threshold" query (public constant).
/// Users with age > 18 are counted.
const AGE_THRESHOLD: i64 = 18;

/// Performs the MPC computation over all submitted secret values.
///
/// This function runs securely across 4 MPC nodes -- no single node
/// ever sees an individual user's value. The result is an aggregate
/// count returned as a secret Sbi64, which is then declassified by
/// the on_compute_complete handler.
///
/// This function handles the "age_threshold" query type:
/// counts how many secret values are strictly greater than 18.
///
/// For "survey_match" queries, the contract dispatches to
/// `compute_survey_sum` instead (see below).
#[zk_compute(shortname = 0x61)]
pub fn compute_aggregate() -> Sbi64 {
    let threshold: Sbi64 = Sbi64::from(AGE_THRESHOLD);
    let mut count: Sbi64 = Sbi64::from(0);
    let one: Sbi64 = Sbi64::from(1);

    for variable_id in secret_variable_ids() {
        if load_metadata::<u8>(variable_id) == USER_VALUE_KIND {
            let value: Sbi64 = load_sbi::<Sbi64>(variable_id);

            // Count values strictly greater than the age threshold.
            // The comparison returns a secret boolean (Sbi1).
            // In the real ZK runtime, this branches on secret booleans.
            let exceeds_threshold: Sbi64 =
                if value > threshold { one } else { Sbi64::from(0) };
            count = count + exceeds_threshold;
        }
    }

    count
}

/// Sums all user-submitted secret values directly.
///
/// Used for "survey_match" queries where each secret is 0 or 1.
/// The result is the total count of users who answered "yes" (1).
///
/// Like `compute_aggregate`, this runs securely across MPC nodes —
/// no single node ever sees an individual user's value.
#[zk_compute(shortname = 0x62)]
pub fn compute_survey_sum() -> Sbi64 {
    let mut sum: Sbi64 = Sbi64::from(0);

    for variable_id in secret_variable_ids() {
        if load_metadata::<u8>(variable_id) == USER_VALUE_KIND {
            let value: Sbi64 = load_sbi::<Sbi64>(variable_id);
            sum = sum + value;
        }
    }

    sum
}
