----------------------------- MODULE TEMPLATE -----------------------------
EXTENDS Integers, Sequences

(*
  @Persona: Scope 🔬
  @Purpose: Formal Verification of Critical State Machines.
  @Usage:
    1. Define the system's state variables (VARIABLES ...).
    2. Define the Type Invariant (TypeOK) to constrain variable types.
    3. Define the Initial State (Init).
    4. Define the State Transitions (Next).
    5. Define Temporal Properties (Spec).
    6. Run TLC Model Checker to prove absence of deadlocks and invariant violations.
*)

CONSTANT
    Users,      (* Set of User IDs *)
    MaxRetries  (* Maximum login attempts *)

VARIABLES
    is_logged_in, (* Function mapping User -> Boolean *)
    login_attempts (* Function mapping User -> Integer *)

(* Invariants *)
TypeOK ==
    /\ is_logged_in \in [Users -> BOOLEAN]
    /\ login_attempts \in [Users -> 0..MaxRetries]

(* Initial State *)
Init ==
    /\ is_logged_in = [u \in Users |-> FALSE]
    /\ login_attempts = [u \in Users |-> 0]

(* Transitions *)
LoginSuccess(u) ==
    /\ is_logged_in[u] = FALSE
    /\ is_logged_in' = [is_logged_in EXCEPT ![u] = TRUE]
    /\ login_attempts' = [login_attempts EXCEPT ![u] = 0]

LoginFailure(u) ==
    /\ is_logged_in[u] = FALSE
    /\ login_attempts[u] < MaxRetries
    /\ login_attempts' = [login_attempts EXCEPT ![u] = login_attempts[u] + 1]
    /\ UNCHANGED is_logged_in

Next ==
    \E u \in Users : LoginSuccess(u) \/ LoginFailure(u)

(* Specification *)
Spec == Init /\ [][Next]_<<is_logged_in, login_attempts>>

=============================================================================
