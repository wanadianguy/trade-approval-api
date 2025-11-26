# Launch the Project
- Have a docker daemon running.
- From the root directory:
    - Run `bash docker compose -f docker-compose.database.yml up -d`
    - Run `python3 -m venv venv`
    - Run `source venv/bin/activate`
    - Run `pip install -r requirements.txt`
    - Run `python manage.py migrate`
    - Run `python manage.py runserver`

# Functionalities
- Create a new trade (always in draft state)
- Update a trade with restrictions on the action to prevent undesired states. These restrictions respect the workflow provided.
- Get all trades for consultation.
- Get the logs of a trade to see the evolution and changes that were made.
- Compare 2 trades and get the differences. The purpose is to compare 2 versions of the same trade, but you could also compare different trades between them.
- Strong database check to make sure no unwanted states can emerge.
- Adding the currency automatically to the underlying table of currencies to comply with requirements.
- Customized exception classes to make resiliency easier to implement.
- Date check to make sure that Trade Date ≤ Value Date ≤ Delivery Date.

# API Endpoints
- GET http://localhost:8000/swagger/
- GET http://localhost:8000/schema/
- GET http://localhost:8000/trades/
- POST http://localhost:8000/trades/
- PATCH http://localhost:8000/trades/<trade_id>/
- GET http://localhost:8000/trade_logs/<trade_id>/
- POST http://localhost:8000/trades/diff/


# What's next?
- Find a better way to handle JSON format (right now: have to go through strings).
- Work on the http://localhost:8000/trades/diff/ endpoint to make it less strict on the types (related to the first imrpovement listed above).
- Write more tests (unit/e2e/integration/...).
- Write CI config file(s).
- Put app in docker (needs environment variable handling).
- Add endpoint to get trades by state and by id (will be useful for the future frontend).
- Export logs into specific formats (csv, excel, ...).
- Create notifications (email?) (would need to have a list of users to notify).

# Disclosure of the use of generative AI
I mostly used generative AI for debugging purposes.

# Notes
My postman requests are in `trade-approval.postman_collection.json` file for convinience.

Thank you for taking the time to review this project!
![Validus](https://www.validusrm.com/)
