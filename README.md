# Case Based Reaoner For Recommending Covid-19 Policies

This is a API for a case based reasoner that provides policy recommendation in the context of Covid-19 such as lockdown, mask, and vaccine policies. This API allows decision makers to create cases, view them, and submit a query to the reasoner which will return a policy recommendation as well as the top 3 most similar cases. The API is built using fastapi and is deployed on Render.com. The case based reasoner API is connected to a Postgres database that stores the cases. The database and the API are hosted and deployed on Render.com.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You will need to have python 3 and postgres server installed on your machine.

### Installing

To install the project, clone the repository and run the following command in the project directory:

## Create a virtual environment
```
python -m venv venv
```
## Activate virtual environment
```
./venv/Scripts/activate
```
## Install requirements
```
pip install -r requirements.txt
```

## DB and env setup
--------------------
Create a empty database with any suitable name. Edit the .env.example with your db credentials.
-------------------


### Running the project

To run the project, run the following command in the project directory:

```
uvicorn main:app --reload
```

Test the project by going to http://localhost:8000/ in your browser.

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - The library used

## Author

- **Sudan Upadhaya** - [sudan94](https://github.com/sudan94)

## License

This project is licensed under the MIT License.