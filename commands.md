cd "C:\Users\dell\Documents\Autonomize AI\qa_automation_framework"
pytest -v --alluredir=reports/allure-results
pytest --collect-only

allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report

cd docker
docker build -t qa-framework .

docker run --rm -v %cd%/..:/app qa-framework #cmd
docker run --rm -v ${PWD}/..:/app qa-framework #psi

cd docker
docker-compose up --build

docker-compose run test-runner

docker-compose up allure-report