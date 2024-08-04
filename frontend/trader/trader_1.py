import requests
import streamlit as st

st.header("Trader")
st.write(f"You are logged in as {st.session_state.role}.")


def sidebar():
    with st.sidebar:
        st.markdown('# :rainbow[Трейдинг и точка]')


def header():
    with st.header('Трейдинг и точка'):
        st.markdown('# :rainbow[Трейдинг и точка]')


def specific_operations():
    with st.form("specific_operations"):
        with st.container():
            text = st.text_input("Тип операции")
            if st.form_submit_button('Нажать'):
                if text:
                    try:
                        res = requests.get(f'http://127.0.0.1:8000/operations?operation_type={text}')
                        operation = res.json().get('data')[0]
                        operation_translate = {
                            'id': 'Номер',
                            'quantity': 'Количество',
                            'figi': 'Лицо',
                            'instrument_type': 'Тип инструмента',
                            'date': 'Дата',
                            'type': 'Тип операции',
                        }
                        operation_dict = {
                            operation_translate[key]: value
                            for key, value in operation.items()
                        }
                        with st.container():
                            st.dataframe(operation_dict, width=1000)
                    except IndexError as e:
                        st.write('Такой операции нет')
                    except Exception as e:
                        st.write(e)


@st.cache_data(ttl=30)
def get_all_operations():
    res = requests.get('http://127.0.0.1:8000/operations/all_operations')
    return res


def all_operations(func):
    with st.form('all_operations'):
        if st.form_submit_button('Все операции'):
            res = func()
            for i in range(2):
                operations = res.json().get('data')[i]
                operation_translate = {
                    'id': 'Номер',
                    'quantity': 'Количество',
                    'figi': 'Лицо',
                    'instrument_type': 'Тип инструмента',
                    'date': 'Дата',
                    'type': 'Тип операции',
                }
                operation_dict = {
                    operation_translate[key]: value
                    for key, value in operations.items()
                }
                with st.container():
                    st.dataframe(operations, width=1000)


def get_email_dashboard():
    # res = requests.get('http://127.0.0.1:8000/report/dashboard')
    if st.button('Отправить письмо'):
        pass
# st.write(res)
# {
#   "email": "timur@gmail.com",
#   "password": "string",
#   "is_active": true,
#   "is_superuser": false,
#   "is_verified": false,
#   "username": "timur",
#   "role_id": 0
# }


def main():
    specific_operations()
    all_operations(get_all_operations)
    get_email_dashboard()


main()
