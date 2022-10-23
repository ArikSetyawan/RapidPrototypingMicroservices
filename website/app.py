from flask import Flask, render_template, request, redirect, url_for, session
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'This is very secret'

API_GATEWAY = "http://127.0.0.1:5000/"

@app.route('/')
def index():
    if 'login' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

# Login
@app.route('/login',methods=['GET',"POST"])
def login():
    if request.method == 'GET':
        if 'login' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']

        auth = requests.post(f"{API_GATEWAY}/login", json={"email":email,"password":password})
        if auth.status_code != 200:
            return redirect(url_for('login'))
        
        auth_data = auth.json()['data']
        session['login'] = True
        session['access_token'] = auth_data['Token']['access_token']
        session['refresh_token'] = auth_data['Token']['refresh_token']
        session['id_user'] = auth_data['User']['id']
        session['email'] = auth_data['User']['email']
        session['team_id'] = auth_data['User']['team_id']

        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

################################## CES ##################################
@app.route('/ces')
def cescontroller():
    if 'login' not in session:
        return redirect(url_for('login'))

    ces = requests.get(f"{API_GATEWAY}/ces", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    ces = ces.json()["data"]
    return render_template("ces.html", ces=ces)

@app.route("/ces/create_cause", methods=['POST'])
def cescausecontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    if name == "":
        return redirect(url_for('cescontroller'))
    
    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":1,
        "name":name
    }
    new_cause = requests.post(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('cescontroller'))

@app.route("/ces/create_effect", methods=['POST'])
def ceseffectcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    cause_id = request.form['cause']
    if name == "":
        return redirect(url_for('cescontroller'))
    
    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":2,
        'cause_id':cause_id,
        "name":name
    }
    new_effect = requests.post(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('cescontroller'))

@app.route("/ces/create_solution", methods=['POST'])
def cessolutioncontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    effect_id = request.form['effect']
    if name == "":
        return redirect(url_for('cescontroller'))
    
    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":3,
        'effect_id':effect_id,
        "name":name
    }
    new_solution = requests.post(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    print(new_solution.json())
    return redirect(url_for('cescontroller'))

################################## FNF ##################################
@app.route('/fnf')
def fnfcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    # Get fnf
    fnf = requests.get(f"{API_GATEWAY}/fnf", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    fnf = fnf.json()['data']
    return render_template('fnf.html',fnf=fnf)

@app.route("/fnf/create_functional", methods=['POST'])
def fnffunctionalcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    if name == "":
        return redirect(url_for('fnfcontroller'))
    
    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":1,
        "name":name
    }
    new_fn = requests.post(f"{API_GATEWAY}/fnf", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('fnfcontroller'))

@app.route("/fnf/create_nonfunctional", methods=['POST'])
def fnfnonfunctionalcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    if name == "":
        return redirect(url_for('fnfcontroller'))
    
    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":2,
        "name":name
    }
    new_nf = requests.post(f"{API_GATEWAY}/fnf", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('fnfcontroller'))

################################## BMC ##################################
@app.route('/bmc')
def bmccontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    bmc = requests.get(f"{API_GATEWAY}/bmc", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    bmc = bmc.json()['data']
    bmc_titles = ["Value Propositions", "Customer Segments", "Customer Relationships", "Channels", "Key Activities", "Key Resources", "Key Partners", "Cost Structures", "Revenue Streams"]
    return render_template("bmc.html",bmc=bmc, bmc_titles=bmc_titles)

@app.route('/bmc/add_item', methods=['POST'])
def bmcaddcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    type = request.form['type']

    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":type,
        "name":name
    }

    new_bmc = requests.post(f"{API_GATEWAY}/bmc", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('bmccontroller'))

@app.route('/bmc/print')
def bmcprint():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    bmc = requests.get(f"{API_GATEWAY}/bmc", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    bmc = bmc.json()['data']
    return render_template("bmc_print.html",bmc=bmc)
################################## PDC ##################################
@app.route('/pdc')
def pdccontroller():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    pdc = requests.get(f"{API_GATEWAY}/pdc", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    pdc = pdc.json()['data']
    pdc_titles = ["Platform Owners", "Platform Stakeholders", "Peers", "Partners", "Transactions", "Channel and Contexts", "Services", "Value Propositions", "Infrastructure and Components"]
    return render_template("pdc.html",pdc=pdc, pdc_titles=pdc_titles)

@app.route('/pdc/add_item', methods=['POST'])
def pdcaddcontroller():
    if 'login' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    type = request.form['type']

    data = {
        "kodekelompok": session['team_id'],
        "backlog":session['email'],
        "type":type,
        "name":name
    }

    new_pdc = requests.post(f"{API_GATEWAY}/pdc", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('pdccontroller'))


if __name__ == '__main__':
    app.run(debug=True, port=5010)