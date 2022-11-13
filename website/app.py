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

@app.route('/ces/print')
def cesprint():
    if 'login' not in session:
        return redirect(url_for('login'))

    ces = requests.get(f"{API_GATEWAY}/ces", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    ces = ces.json()["data"]
    return render_template("ces_print.html", ces=ces)

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

@app.route('/ces/edit_cause/<cause_id>', methods=['POST'])
def editcause(cause_id):
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    data ={
        "cause_id":cause_id,
        "name":name
    }

    edit_cause = requests.put(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('cescontroller'))

@app.route('/ces/delete_cause/<cause_id>')
def deletecause(cause_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_cause = requests.delete(f"{API_GATEWAY}/ces", params={"cause_id":cause_id}, headers={"Token":session['access_token']})
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

@app.route('/ces/edit_effect/<effect_id>', methods=['POST'])
def editeffect(effect_id):
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    data ={
        "effect_id":effect_id,
        "name":name
    }

    edit_effect = requests.put(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('cescontroller'))

@app.route('/ces/delete_effect/<effect_id>')
def deleteeffect(effect_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_effect = requests.delete(f"{API_GATEWAY}/ces", params={"effect_id":effect_id}, headers={"Token":session['access_token']})
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
    return redirect(url_for('cescontroller'))

@app.route('/ces/edit_solution/<solution_id>', methods=['POST'])
def editsolution(solution_id):
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    data ={
        "solution_id":solution_id,
        "name":name
    }

    edit_solution = requests.put(f"{API_GATEWAY}/ces", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('cescontroller'))

@app.route('/ces/delete_solution/<solution_id>')
def deletesolution(solution_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_solution = requests.delete(f"{API_GATEWAY}/ces", params={"solution_id":solution_id}, headers={"Token":session['access_token']})
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

@app.route('/fnf/print')
def fnfprint():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    # Get fnf
    fnf = requests.get(f"{API_GATEWAY}/fnf", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    fnf = fnf.json()['data']
    return render_template('fnf_print.html',fnf=fnf)

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

@app.route('/fnf/edit/<fnf_id>', methods=['POST'])
def editfnf(fnf_id):
    if 'login' not in session:
        return redirect(url_for('login'))
        
    name = request.form['name']
    description = request.form['description']
    assign_to = request.form['assign_to']
    target_finish = request.form['target_finish']
    data = {
        "fnf_id":fnf_id,
        "name":name,
        "description":description,
        "assign_to":assign_to,
        "target_finish":target_finish
    }
    edit_nf = requests.put(f"{API_GATEWAY}/fnf", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('fnfcontroller'))

@app.route('/fnf/delete/<fnf_id>')
def deletefnf(fnf_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_fnf = requests.delete(f"{API_GATEWAY}/fnf", params={"fnf_id":fnf_id}, headers={"Token":session['access_token']})
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

@app.route('/bmc/edit/<bmc_id>', methods=['POST'])
def editbmc(bmc_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    data = {
        "bmc_id":bmc_id,
        "name":name
    }

    update_bmc = requests.put(f"{API_GATEWAY}/bmc", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('bmccontroller'))

@app.route('/bmc/delete/<bmc_id>')
def deletebmc(bmc_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_bmc = requests.delete(f"{API_GATEWAY}/bmc", params={"bmc_id":bmc_id}, headers={"Token":session['access_token']})
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

@app.route('/pdc/print')
def pdcprint():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    pdc = requests.get(f"{API_GATEWAY}/pdc", params={"kodekelompok":session['team_id']}, headers={"Token":session['access_token']})
    pdc = pdc.json()['data']
    return render_template("pdc_print.html",pdc=pdc)

@app.route('/pdc/edit/<pdc_id>', methods=['POST'])
def editpdc(pdc_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    name = request.form['name']
    data = {
        "pdc_id":pdc_id,
        "name":name
    }

    update_pdc = requests.put(f"{API_GATEWAY}/pdc", json=data, headers={"Token":session['access_token']})
    return redirect(url_for('pdccontroller'))

@app.route('/pdc/delete/<pdc_id>')
def deletepdc(pdc_id):
    if 'login' not in session:
        return redirect(url_for('login'))

    delete_pdc = requests.delete(f"{API_GATEWAY}/pdc", params={"pdc_id":pdc_id}, headers={"Token":session['access_token']})
    return redirect(url_for('pdccontroller'))

if __name__ == '__main__':
    app.run(debug=True, port=5010)