# Vars
from datetime import datetime
from flask import render_template,request,session
import requests
from getpeering import app
import json

################################################################## SUPPORTING FUNCTIONS #################################################
def get_peering_info(asn_num):
    """

        asn_peering_dict['{ip_prefix}'] = [{peer_name},{speed}]
    """
    # Vars
    asn_peering_dict = {}
    peering_cnt = 0
    total_agg_speed = 0

    # API Call
    response = requests.get("https://peeringdb.com/api/netixlan.json?asn={}".format(asn_num))
    json_output = response.json()

    # Iterate over API info and add each prefix to custom dict
    for each_prefix in json_output['data']:
        ip_prefix = each_prefix['ipaddr4']
        peer_name = each_prefix['name']
        speed = str(int(each_prefix['speed'])/1000) + " Gbps"
        # Append prefix info to Peer Name
        if peer_name not in asn_peering_dict:
            asn_peering_dict[peer_name] = []
        asn_peering_dict[peer_name].append([ip_prefix,speed])
        # Increment peerign_cnt and aggregate_speed
        peering_cnt += 1
        total_agg_speed += (int(each_prefix['speed'])/1000)

    # Return custom dict for HTML display
    return (asn_peering_dict,str(peering_cnt),str(total_agg_speed))



def get_co_info(asn_num):
    """

    """

    # API Call
    response = requests.get("https://peeringdb.com/api/net?asn={}".format(asn_num))
    json_output = response.json()  
    co_name = json_output['data'][0]['name']
    co_website = json_output['data'][0]['website']
    # Return info requested
    return (co_name,co_website)




###################################################################### ROUTES ############################################################
# Home Page
@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
        action="/verify-company"
    )


# Verify Company
@app.route('/verify-company',methods = ['POST', 'GET'])
def company_info():
    """ Pulls in data from user to get company info """

    if request.method == 'POST':
        user_vars = request.form
        asn_num = user_vars['asn_num']
        session['asn_num'] = asn_num

        if asn_num == '':
            return render_template('index.html',
                                    title='Home Page',
                                    year=datetime.now().year,
                                    action="/verify-company",
                                    error_type = "null")       
        else:
            # Get Company Info
            try:
                co_name,co_website = get_co_info(asn_num)
            except:
                # Return homepage to get BGP ASN if there is no record of orginal request
                return render_template('index.html',
                                       title='Home Page',
                                       year=datetime.now().year,
                                       action="/verify-company",
                                       error_type = "bad_asn")       

            # Get peering info from peeringdb.com API
            asn_peering_dict,peering_cnt,total_agg_speed = get_peering_info(asn_num)
            session['asn_peering_dict'] = asn_peering_dict
            return render_template('company-info.html',
                                    year=datetime.now().year,
                                    company_name = co_name,
                                    company_website = co_website,
                                    bgp_asn = asn_num,
                                    prefix_num = peering_cnt,
                                    total_bandwidth = total_agg_speed + " Gbps",
                                    action="peering_info")


# Peering Info Page
@app.route('/peering-info')
def peering():
    """Renders the BGP peering information home page after customer puts in
       BGP ASN and/or Company name"""

    # Return Peering info via HTML page
    return render_template('peering-info.html',
                            title='Home Page',
                            year=datetime.now().year,
                            asn_peering_dict = session.get('asn_peering_dict'),
                            bgp_asn = session.get('asn_num'),
                            action="/peering-info")
 
          
# Contact Page
@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )


# About Page
@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
