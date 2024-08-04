import requests
import streamlit as st


def base():
    if "role" not in st.session_state:
        st.session_state.role = None

    ROLES = [None, "Trader", "Admin"]

    def login():
        st.header("Log in")
        role = st.selectbox("Choose your role", ROLES)

        if st.button("Log in"):
            # res = requests.post('http://127.0.0.1:8000/auth/jwt/login?username=timur@gmail.com&password=string')
            # st.write(res)
            st.session_state.role = role
            st.rerun()

    def logout():
        st.session_state.role = None
        st.rerun()

    role = st.session_state.role
    logout_page = st.Page(logout,
                          title="Log out",
                          icon=":material/logout:")
    settings = st.Page("settings.py",
                       title="Settings",
                       icon=":material/settings:")

    trader_1 = st.Page(
        "trader/trader_1.py",
        title="Trader",
        icon=":material/healing:",
        default=(role == "Trader"),
    )

    admin_1 = st.Page(
        "admin/admin_1.py",
        title="Admin",
        icon=":material/person_add:",
        default=(role == "Admin"),
    )

    account_pages = [logout_page, settings]
    trader_pages = [trader_1]
    admin_pages = [admin_1]

    st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")
    page_dict = {}
    if st.session_state.role in ["Trader", "Admin"]:
        page_dict["Trader"] = trader_pages
    if st.session_state.role == "Admin":
        page_dict["Admin"] = admin_pages

    if len(page_dict) > 0:
        pg = st.navigation({"Account": account_pages} | page_dict)
    else:
        pg = st.navigation([st.Page(login)])
    pg.run()


def main():
    base()


if __name__ == '__main__':
    main()
