cp /solution/solve.sh /tmp/solve.sh
sed -i 's/\r$//' /tmp/solve.sh
bash /tmp/solve.sh
cd /workspace/repo
echo "--- files:"
ls
echo "--- py files left:"
find . -name "*.py"
echo "--- go build ./...:"
go build ./... && echo BUILD_OK
echo "--- go build . (root):"
go build -o /tmp/tc . && echo ROOT_BUILD_OK
/tmp/tc < /data/hidden_inputs.txt > /tools/out/out.txt
echo "rc=$?"
wc -l /tools/out/out.txt