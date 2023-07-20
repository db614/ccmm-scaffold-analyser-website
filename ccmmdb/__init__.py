from ccmmdb.core.app import create_app

__version__ = '0.0.dev0'

app = create_app()

if __name__=="__main__":
    app.run()
    # Create a self signed certificate while testing as OAuth2 requires https:
    #context = ('cert.pem', 'key.pem')
    #app.run(ssl_context = 'adhoc')

