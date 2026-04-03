# demo

## steps
```shell
# 1. create form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_create_form" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v
# 2. fill form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testT4279" --env release --yaml Partner_create_form.yaml --headed -v
```