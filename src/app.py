from page_builders import build_page
from authentication import check_password

if check_password():
    build_page()
