call conda info --envs | find /i "balance"
if errorlevel 1 (
   call conda create -n balance python==3.9 -y
)
call conda activate balance && pip install -r ../Dash/requirements.txt
cd ..\Dash && python report_account.py