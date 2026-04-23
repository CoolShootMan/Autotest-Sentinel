# demo
- demi test


## steps
```shell
# 1. create form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_create_form" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v
# 2. fill form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "test_guest_submission_1" --env release --yaml Partner_create_form.yaml --headed -v
# 3. verify
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_verify_commission" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v


# all in one
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_create_form or testPartner_guest_submission or testPartner_verify_commission" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v
```

# main.py
```shell
$ python main.py
```