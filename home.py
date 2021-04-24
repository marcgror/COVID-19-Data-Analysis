import streamlit as st
import awesome_streamlit as ast
import COVID

st.set_page_config(layout='wide')

PAGES =  {
    'COVID': COVID,

}

def main():
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio('Go to', list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f'Loading {selection} ...'):
        ast.shared.components.write_page(page)

if __name__ == "__main__":
    main()