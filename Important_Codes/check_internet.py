import speedtest

def check_upload_download():
    st = speedtest.Speedtest(secure=True)
    print(st.download())  
    print(st.upload())

check_upload_download()