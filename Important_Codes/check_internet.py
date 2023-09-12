import speedtest

def check_upload_download():
    st = speedtest.Speedtest(timeout=1)
    print(st.download())  
    print(st.upload())

check_upload_download()