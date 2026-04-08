# demo

## topics
```txt
Aric and Yuxiao to prepare:
1. Explain what has been covered in the Form auto tests
2. Run the demo
3. Run a demo of the process to add a new test case

What's the benefit and impact
Discussion:
1. Is this useful - can it replace Aric's manual self testing
2. Would you use it
- If Yes: how to make it better
- If no: what's the issue
```

## steps
```shell
# 1. create form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_create_form" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v
# 2. fill form
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_guest_submission" --env release --yaml Partner_create_form.yaml --headed -v
# 3. verify
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_verify_commission" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v


# all in one
$ pytest test_case/UI/Test_Katana/test_ui.py -k "testPartner_create_form or testPartner_guest_submission or testPartner_verify_commission" --storage-state "test_case/UI/Test_Katana/cookie_release.json" --env release --yaml Partner_create_form.yaml --headed -v
```

# main.py
```shell
# not work on macos
$ python main.py
```

## start a new case
1. 使用 `playwright codegen --device "Desktop Chrome" https://release.pear.us/demi-release`
2. 录制完成之后，交给 `AI`
3. 如果出现 `id` 之类的，需要重构，修改成合适的 - 这一步也可以交给AI

## make it better
1. autotest monster 应该是一个 `cli` + 一个管理界面
2. 前期可以是一个 `cli`，对于一切人员，只关心 `generate cases`
3. 不同的模块，有不同的目录来管理 case - 最终可以选择入库(ps: yaml可以直接入库)
4. windows/mac 可以正常运行(目前环境这块还存在小问题)