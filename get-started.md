# get-started

## setup env
```sh
cd ~/your-project-dir/Autotest-monster
pip install -r requirements.txt

## env activate
source .venv/bin/activate
```

## 如何录制
1. 确认有 playwright 命令
2. 录制命令 `playwright codegen 目录URL`(不需要登录等场景的)

## 运行单个 case
```sh
pytest test_case/UI/Test_Katana/test_ui.py -k "testT4279" --headed -v --env release --storage-state test_case/UI/Test_Katana/cookie_release.json
```
