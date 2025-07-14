from flask import Flask, render_template, request
import re

app = Flask(__name__)

def convert_currency(amount, currency):
    if currency == 'EGP':
        converted = (amount / 49.00) * 1.025 * 3.75
    elif currency == 'IQD':
        converted = (amount / 3500) * 1.025
    elif currency == 'USD':
        converted = (amount / 0.2666666) * 1.027
    elif currency == 'MVR':
        converted = (amount / 4.09) * 1.025
    elif currency == 'JPY':
        converted = (amount * 0.00703) * 1.025 * 3.76
    elif currency == 'SAR':
        converted = amount * 1.025
    else:
        converted = amount  # Default to no conversion if currency is not recognized
    return round(converted, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    raw_data = request.form['data']
    results = []
    total_converted_amount = 0  # لاحتساب مجموع المبالغ المحولة

    # تحليل النصوص الجديدة باستخدام regex
    pattern_new = re.compile(r'شراء (.*?)\s+عبر:(.*?)\s+بـ:(.*?)\s+(.*?)\s+من:(.*?)\s+في:\s+(.*)')
    matches_new = pattern_new.findall(raw_data)

    for match in matches_new:
        entry_data = {}
        entry_data['card'] = match[1].strip()
        entry_data['amount'] = float(match[2].strip())
        entry_data['currency'] = match[3].strip()
        entry_data['merchant'] = match[4].strip()
        entry_data['date'] = match[5].strip()

        # تحويل العملة
        converted_amount = convert_currency(entry_data['amount'], entry_data['currency'])
        entry_data['converted_amount'] = converted_amount
        
        # حساب المبلغ بالمصري
        egyptian_amount = (converted_amount / 3.75) * 50.30
        entry_data['egyptian_amount'] = round(egyptian_amount, 2)
        
        total_converted_amount += converted_amount

        results.append(entry_data)

    # تحليل النصوص القديمة (مشتريات إنترنت)
    entries_old = raw_data.split('مشتريات إنترنت')
    
    for entry in entries_old:
        lines = entry.strip().split('\n')
        entry_data = {}
        
        for line in lines:
            if 'البطاقة' in line:
                entry_data['card'] = line.split(': ')[1].strip()
            elif 'المبلغ' in line:
                amount_currency = line.split(': ')[1].strip().split(' ')
                amount = amount_currency[0]
                currency = amount_currency[1] if len(amount_currency) > 1 else ''
                entry_data['amount'] = float(amount)
                entry_data['currency'] = currency
            elif 'في' in line:
                entry_data['merchant'] = line.split(': ')[1].strip()
            elif 'من حساب رقم' in line:
                entry_data['account'] = line.split(': ')[1].strip()
            elif 'بتاريخ' in line:
                entry_data['date'] = line.split(': ')[1].strip()

        # تحويل العملة في النصوص القديمة
        if 'amount' in entry_data and 'currency' in entry_data:
            converted_amount = convert_currency(entry_data['amount'], entry_data['currency'])
            entry_data['converted_amount'] = converted_amount
            
            # حساب المبلغ بالمصري
            egyptian_amount = (converted_amount / 3.75) * 50.30
            entry_data['egyptian_amount'] = round(egyptian_amount, 2)
            
            total_converted_amount += converted_amount
            results.append(entry_data)

    return render_template('result.html', results=results, total_converted_amount=total_converted_amount)

if __name__ == '__main__':
    app.run(debug=True)
