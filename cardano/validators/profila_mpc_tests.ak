use aiken/crypto.{VerificationKeyHash}
use cardano/transaction.{Transaction, placeholder}
use profila_mpc.{MpcAction, MpcRequest, is_valid_query_type}

// ---------------------------------------------------------------------------
// Test Helpers
// ---------------------------------------------------------------------------

/// A known test PKH (28 bytes / 56 hex chars, matching Cardano key hash length)
const test_pkh: VerificationKeyHash =
  #"aabbccddaabbccddaabbccddaabbccddaabbccddaabbccddaabbccdd"

/// A different PKH that does NOT match the test signer
const wrong_pkh: VerificationKeyHash =
  #"11223344112233441122334411223344112233441122334411223344"

/// Build a valid MpcRequest for testing
fn valid_request() -> MpcRequest {
  MpcRequest {
    dataset_id: "profila_test_001",
    query_type: "age_threshold",
    initiator_pkh: test_pkh,
    partisia_contract: "",
    timestamp: 1_700_000_000_000,
  }
}

/// Build a transaction where test_pkh has signed
fn tx_with_signer() -> Transaction {
  Transaction { ..placeholder, extra_signatories: [test_pkh] }
}

// ---------------------------------------------------------------------------
// Test 1: Valid MPC Initiation (happy path)
// ---------------------------------------------------------------------------

test test_initiate_mpc_valid() {
  let request = valid_request()
  let tx = tx_with_signer()
  let datum = Some(request)
  let redeemer = MpcAction.InitiateMPC
  let utxo =
    transaction.OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: 0,
    }
  profila_mpc.profila_mpc.spend(datum, redeemer, utxo, tx)
}

// ---------------------------------------------------------------------------
// Test 2: Empty dataset_id should FAIL
// ---------------------------------------------------------------------------

test test_initiate_mpc_empty_dataset() fail {
  let request = MpcRequest { ..valid_request(), dataset_id: "" }
  let tx = tx_with_signer()
  let datum = Some(request)
  let redeemer = MpcAction.InitiateMPC
  let utxo =
    transaction.OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: 0,
    }
  profila_mpc.profila_mpc.spend(datum, redeemer, utxo, tx)
}

// ---------------------------------------------------------------------------
// Test 3: Wrong signer (PKH not in extra_signatories) should FAIL
// ---------------------------------------------------------------------------

test test_initiate_mpc_wrong_signer() fail {
  let request = MpcRequest { ..valid_request(), initiator_pkh: wrong_pkh }
  let tx = tx_with_signer()
  let datum = Some(request)
  let redeemer = MpcAction.InitiateMPC
  let utxo =
    transaction.OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: 0,
    }
  // tx has test_pkh signed, but request has wrong_pkh as initiator
  profila_mpc.profila_mpc.spend(datum, redeemer, utxo, tx)
}

// ---------------------------------------------------------------------------
// Test 4: Bad query_type should FAIL
// ---------------------------------------------------------------------------

test test_initiate_mpc_bad_query() fail {
  let request =
    MpcRequest { ..valid_request(), query_type: "invalid_query_type" }
  let tx = tx_with_signer()
  let datum = Some(request)
  let redeemer = MpcAction.InitiateMPC
  let utxo =
    transaction.OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: 0,
    }
  profila_mpc.profila_mpc.spend(datum, redeemer, utxo, tx)
}

// ---------------------------------------------------------------------------
// Test 5: Zero/negative timestamp should FAIL
// ---------------------------------------------------------------------------

test test_initiate_mpc_bad_timestamp() fail {
  let request = MpcRequest { ..valid_request(), timestamp: 0 }
  let tx = tx_with_signer()
  let datum = Some(request)
  let redeemer = MpcAction.InitiateMPC
  let utxo =
    transaction.OutputReference {
      transaction_id: #"0000000000000000000000000000000000000000000000000000000000000000",
      output_index: 0,
    }
  profila_mpc.profila_mpc.spend(datum, redeemer, utxo, tx)
}

// ---------------------------------------------------------------------------
// Test 6: Utility — is_valid_query_type
// ---------------------------------------------------------------------------

test test_valid_query_types() {
  is_valid_query_type("age_threshold") && is_valid_query_type("survey_match") && !is_valid_query_type(
    "unknown",
  )
}
