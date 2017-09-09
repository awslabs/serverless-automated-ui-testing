#!/usr/bin/env python

from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from botocore.exceptions import ClientError
import requests
import traceback
import os
import boto3
import inspect
import sys
import random


br = os.environ['BROWSER']
main_url = os.environ['WebURL']
module_table = os.environ['ModuleTable']
status_table = os.environ['StatusTable']
s3_output_bucket = os.environ['ArtifactBucket']
ddb = boto3.client('dynamodb')
s3 = boto3.client('s3')
s3_path_prefix = os.environ['CODEBUILD_BUILD_ID'].replace(':', '/')


def funcname():
    return inspect.stack()[1][3]


def update_status(mod, tc, st, et, ss, er):
    if et != ' ':
        t_t = str(int(round((datetime.strptime(et, '%d-%m-%Y %H:%M:%S,%f') -
                             datetime.strptime(st, '%d-%m-%Y %H:%M:%S,%f')).microseconds, -3) / 1000))
    else:
        t_t = ' '
    try:
        if er:
            ddb.update_item(Key={'module': {'S': mod}, 'testcaseid': {'S': br + '-' + tc}},
                            UpdateExpression="set details.StartTime = :st, details.EndTime = :e, details.#S = :s," +
                            "details.ErrorMessage = :er, details.TimeTaken = :tt",
                            ExpressionAttributeValues={':e': {'S': et}, ':s': {'S': ss}, ':st': {'S': st},
                                                       ':er': {'S': er}, ':tt': {'S': t_t}},
                            TableName=status_table, ExpressionAttributeNames={'#S': 'Status'})
        else:
            ddb.update_item(Key={'module': {'S': mod}, 'testcaseid': {'S': br + '-' + tc}},
                            UpdateExpression="set details.StartTime = :st, details.EndTime = :e, details.#S = :s," +
                                             "details.TimeTaken = :tt",
                            ExpressionAttributeValues={':e': {'S': et}, ':s': {'S': ss}, ':st': {'S': st},
                                                       ':tt': {'S': t_t}},
                            TableName=status_table, ExpressionAttributeNames={'#S': 'Status'})
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException':
            ddb.update_item(Key={'module': {'S': mod}, 'testcaseid': {'S': br + '-' + tc}},
                            UpdateExpression="set #atName = :atValue", ExpressionAttributeValues={
                            ':atValue': {'M': {'StartTime': {'S': st}, 'EndTime': {'S': et}, 'Status': {'S': ss},
                                               'ErrorMessage': {'S': er}, 'TimeTaken': {'S': t_t}}}},
                            TableName=status_table,
                            ExpressionAttributeNames={'#atName': 'details'})
        else:
            traceback.print_exc()
    except:
        traceback.print_exc()


def tc001(browser, mod, tc):
    # Testcase to validate whether home page is displayed properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc002(browser, mod, tc):
    # Testcase to validate whether button click is displayed properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    todisplay = 'AWS CodeBuild is a fully managed build service that compiles source code,' + \
                ' runs tests, and produces software packages that are ready to deploy.'
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='bc']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'displaybtn')))
        assert 'AWS CodeBuild automation - Button Click.' in browser.title
        browser.find_element_by_id('displaybtn').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element_by_id('cbbutton').text
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        if todisplay == displayed:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Passed', ' ')
        else:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Didn\'t find the expected text to be displayed.')
            return -1
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc003(browser, mod, tc):
    # Testcase to validate whether reset button is working properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='bc']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'displaybtn')))
        assert 'AWS CodeBuild automation - Button Click.' in browser.title
        browser.find_element_by_id('displaybtn').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element_by_id('cbbutton').text
        browser.find_element_by_id('resetbtn').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbutton')))
        displayed = browser.find_element_by_id('cbbutton').text
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        if displayed:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Text was not reset as expected.')
            return -1
        else:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc004(browser, mod, tc):
    # Testcase to validate whether check box is working properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='cb']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'box3')))
        assert 'AWS CodeBuild automation - Check Box.' in browser.title
        browser.find_element_by_id('box1').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbox1')))
        displayed = browser.find_element_by_id('cbbox1').text
        if displayed != 'Checkbox 1 checked.':
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Checkbox1 text was not displayed.')
            return -1
        browser.find_element_by_id('box2').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'cbbox2')))
        displayed = browser.find_element_by_id('cbbox2').text
        if displayed != 'Checkbox 2 checked.':
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Checkbox2 text was not displayed.')
            return -1
        browser.find_element_by_id('box1').click()
        WebDriverWait(browser, 20).until_not(EC.visibility_of_element_located((By.ID, 'cbbox1')))
        displayed = browser.find_element_by_id('cbbox1').text
        if displayed:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Checkbox1 text was displayed after unchecking.')
            return -1
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc005(browser, mod, tc):
    # Testcase to validate whether dropdown is working properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='dd']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.NAME, 'cbdropdown')))
        assert 'AWS CodeBuild automation - Dropdown.' in browser.title
        browser.find_element_by_id('CP').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        cp_text = 'AWS CodePipeline is a continuous integration and continuous delivery service ' + \
                  'for fast and reliable application and infrastructure updates.'
        if displayed != cp_text:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected text for CodePipeline' +
                          'from dropdown was not displayed.')
            return -1
        browser.find_element_by_id('CC').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        cc_text = 'AWS CodeCommit is a fully-managed source control service that makes it easy for ' + \
                  'companies to host secure and highly scalable private Git repositories.'
        if displayed != cc_text:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected text for CodeCommit' +
                          'from dropdown was not displayed.')
            return -1
        browser.find_element_by_id('CB').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        cb_text = 'AWS CodeBuild is a fully managed build service that compiles source code, ' + \
                  'runs tests, and produces software packages that are ready to deploy.'
        if displayed != cb_text:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected text for CodeBuild' +
                          'from dropdown was not displayed.')
            return -1
        browser.find_element_by_id('CD').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        cd_text = 'AWS CodeDeploy is a service that automates code deployments to any instance, ' + \
                  'including Amazon EC2 instances and instances running on-premises.'
        if displayed != cd_text:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected text for CodeDeploy' +
                          'from dropdown was not displayed.')
            return -1
        browser.find_element_by_id('CS').click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        cs_text = 'AWS CodeStar enables you to quickly develop, build, and deploy applications on AWS. ' + \
                  'AWS CodeStar provides a unified user interface, enabling you to easily manage your ' + \
                  'software development activities in one place.'
        if displayed != cs_text:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected text for CodeStar' +
                          'from dropdown was not displayed.')
            return -1
        browser.find_element_by_id('emp').click()
        # WebDriverWait(browser, 120).until(EC.visibility_of_element_located((By.ID, 'dvidrop')))
        displayed = browser.find_element_by_id('dvidrop').text
        if displayed:
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected no text')
            return -1
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc006(browser, mod, tc):
    # Testcase to validate whether images page is working properly
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='img']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'image1')))
        assert 'AWS CodeBuild automation - Images.' in browser.title
        image_list = browser.find_elements_by_tag_name('img')
        for image in image_list:
            imageurl = image.get_attribute('src')
            imgfile = imageurl.split('/')[-1]
            img_res = requests.head(imageurl)
            if img_res.status_code != 200 and (img_res.status_code == 403 and imgfile != 'test3.png'):
                endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
                update_status(mod, tc, starttime, endtime, 'Failed', 'Expected images not displayed.')
                return -1
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def tc007(browser, mod, tc):
    # Testcase to validate whether keypress page is working properly
    key_pos = [Keys.ALT, Keys.CONTROL, Keys.DOWN, Keys.ESCAPE, Keys.F1, Keys.F10, Keys.F11, Keys.F12, Keys.F2,
               Keys.F3, Keys.F4, Keys.F5, Keys.F6, Keys.F7, Keys.F8, Keys.F9, Keys.LEFT, Keys.SHIFT, Keys.SPACE,
               Keys.TAB, Keys.UP]
    key_word = ['ALT', 'CONTROL', 'DOWN', 'ESCAPE', 'F1', 'F10', 'F11', 'F12', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7',
                'F8', 'F9', 'LEFT', 'SHIFT', 'SPACE', 'TAB', 'UP']
    fname = mod + '-' + tc + '.png'
    starttime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
    endtime = ' '
    if br == 'firefox':
        print('Skipping this test for FireFox due to gecko driver issue.')
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Skipped', 'Skipping this test for FireFox due' +
                      'to gecko driver issue.')
        return 0
    try:
        update_status(mod, tc, starttime, endtime, 'Started', ' ')
        browser.get(main_url)
        assert 'AWS CodeBuild automation' in browser.title
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'kp')))
        browser.find_element_by_xpath("//*[@id='kp']/a").click()
        WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, 'titletext')))
        assert 'AWS CodeBuild automation - Key Press.' in browser.title
        actions = webdriver.ActionChains(browser)
        actions.move_to_element(browser.find_element_by_id('titletext'))
        actions.click()
        rnum = random.randrange(0, 20)
        actions.send_keys(key_pos[rnum])
        actions.perform()
        WebDriverWait(browser, 5).until(EC.visibility_of_element_located((By.ID, 'keytext')))
        displayed = browser.find_element_by_id('keytext').text
        browser.get_screenshot_as_file(fname)
        with open(fname, 'rb') as data:
            s3.upload_fileobj(data, s3_output_bucket, s3_path_prefix + '/' + fname)
        os.remove(fname)
        if displayed != 'You pressed \'' + key_word[rnum] + '\' key.':
            endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
            update_status(mod, tc, starttime, endtime, 'Failed', 'Expected key press not displayed.')
            return -1
        print('Completed test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Passed', ' ')
    except:
        print('Failed while running test %s' % funcname())
        endtime = datetime.strftime(datetime.today(), '%d-%m-%Y %H:%M:%S,%f')
        update_status(mod, tc, starttime, endtime, 'Failed', traceback.print_exc())
        return -1


def test_phantomjs():
    phantomjs_function = os.environ['PhantomJSFunction']
    mods = os.environ['MODULES'].split(',')
    client = boto3.client('lambda')
    for mod in mods:
        mod_tcs = ddb.get_item(TableName=module_table, Key={'module': {'S': mod.strip()}})['Item']['testcases']['L']
        for tc in mod_tcs:
            tcname = str(tc['S'].strip())
            try:
                response = client.invoke(ClientContext=tcname, FunctionName=phantomjs_function, InvocationType='Event',
                                         Payload="{\"testcase\": \"" + tcname + "\", \"module\": \"" +
                                         mod.strip() + "\"}")
                print(response)
            except:
                print('Failed while invoking test %s' % tcname)
                traceback.print_exc()
                print(traceback.print_exc())


if __name__ == '__main__':
    if br.lower() == 'chrome':
        browser = webdriver.Chrome()
    elif br.lower() == 'firefox':
        browser = webdriver.Firefox()
    elif br.lower() == 'phantomjs':
        test_phantomjs()
        sys.exit(0)
    else:
        print('Unexpected browser value: %s', br)
        sys.exit(-1)
    mods = os.environ['MODULES'].split(',')
    allmthd = globals().copy()
    allmthd.update(locals())
    for mod in mods:
        mod_tcs = ddb.get_item(TableName=module_table, Key={'module': {'S': mod.strip()}})['Item']['testcases']['L']
        for tc in mod_tcs:
            tcname = str(tc['S'].strip())
            method = allmthd.get(tcname)
            if not method:
                raise Exception("Test case %s is not implemented" % tc['S'].strip())
            method(browser, mod.strip(), tcname)

    if browser:
        browser.quit()
