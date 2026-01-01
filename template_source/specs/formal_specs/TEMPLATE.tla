---------------- MODULE TEMPLATE ----------------
(*
    This is a TLA+ specification stub.
    Agents should use this to formally define critical logic.
*)

EXTENDS Integers, Sequences

CONSTANT Users, Data

VARIABLE state

TypeInvariant == state \in {"init", "processing", "done", "error"}

Init == state = "init"

Next ==
    \/ state = "init" /\ state' = "processing"
    \/ state = "processing" /\ state' = "done"

Spec == Init /\ [][Next]_state

==================================================
