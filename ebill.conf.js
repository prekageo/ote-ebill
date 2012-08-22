{
  "rules": [
    "'local' if call['call_group'] == 'AST' else None",
    "'long_distance' if call['call_group'] == 'YPE' else None",
    "'mobile' if call['call_group'] == 'KIN' else None",
    
    "'local' if call['call_group'] == 'ALD' and len(call['callee'])==10 and call['callee'].startswith('21') else None",
    "'long_distance' if call['call_group'] == 'ALD' and len(call['callee'])==10 else None"
  ]
}
