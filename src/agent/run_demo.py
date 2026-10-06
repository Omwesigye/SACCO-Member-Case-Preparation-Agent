from orchestrator import run_case_preparation

scenarios = [
    ("SACCO-M-001", "Scenario A -- complete, well-formed case"),
    ("SACCO-M-999", "Scenario B -- member not found (failure case)"),
    ("SACCO-M-002", "Scenario C -- member found, KYC missing (pending items, still completes)"),
]

with open("execution_traces.txt", "w") as f:
    for member_id, label in scenarios:
        trace = run_case_preparation(member_id)
        f.write(f"\n\n########## {label} ##########\n")
        f.write(trace.to_text())
        print(f"{label}: final status = {trace.status}")

print("\nSaved to execution_traces.txt")
