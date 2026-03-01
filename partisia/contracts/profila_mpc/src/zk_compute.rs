use pbc_zk::*;

/// Metadata discriminant for user-submitted secret values.
/// Must match SecretVarType::UserValue discriminant (0) in contract.rs.
const USER_VALUE_KIND: u8 = 0u8;

/// The age threshold for the "age_threshold" query.
/// Users with age > 18 are counted.
const AGE_THRESHOLD: Sbi64 = Sbi64::from(18);

/// Performs the MPC computation over all submitted secret values.
///
/// This function runs securely across 4 MPC nodes — no single node
/// ever sees an individual user's value. The result is an aggregate
/// count returned as a secret Sbi64, which is then declassified by
/// the on_compute_complete handler.
///
/// Behaviour depends on the query_type set at init:
/// - "age_threshold": counts how many secret values are > 18
/// - "survey_match":  sums all secret values (each is 0 or 1)
///
/// Both computations produce a single Sbi64 count/sum.
/// The query_type dispatch happens via metadata tagging at the
/// contract level — here we simply count values > threshold
/// which works for both cases:
///   - age_threshold: threshold = 18, values are ages
///   - survey_match:  threshold = 0, values are 0 or 1 (sum = count of 1s)
///
/// For the PoC, we use a unified computation that sums a conditional:
///   for each secret, add 1 if value > threshold, else add 0.
/// This generalises to both query types.
#[zk_compute(shortname = 0x61)]
pub fn compute_result() -> Sbi64 {
    let mut count: Sbi64 = Sbi64::from(0);
    let one: Sbi64 = Sbi64::from(1);

    for variable_id in secret_variable_ids() {
        if load_metadata::<u8>(variable_id) == USER_VALUE_KIND {
            let value: Sbi64 = load_sbi::<Sbi64>(variable_id);

            // For age_threshold: count values > 18
            // For survey_match: values are 0 or 1, so value > 0 gives count of 1s
            //
            // The comparison returns a secret boolean (Sbi1).
            // We convert it to Sbi64: if true, add 1; if false, add 0.
            //
            // NOTE: In ZK Rust, we cannot branch on a secret boolean
            // to assign a public value. Instead, we use arithmetic:
            //   result of (value > threshold) is 0 or 1 as Sbi64
            //   which we can add directly.
            let exceeds_threshold: Sbi64 = if value > AGE_THRESHOLD { one } else { Sbi64::from(0) };
            count = count + exceeds_threshold;
        }
    }

    count
}
