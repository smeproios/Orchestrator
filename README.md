gitGraph
  commit id:"init"
  branch guardrails
  commit id:"add-guardrails"
  branch compliance
  commit id:"add-compliance"
  checkout guardrails
  branch routing
  commit id:"add-routing"
  checkout main
  merge guardrails
  merge compliance
  merge routing
  commit id:"wire-orchestrator"
