from hubspot.email_send_status_contacts import get_contacts_email_send_status as base_get_contacts_email_send_status


def get_contacts_email_send_status():
    res = base_get_contacts_email_send_status()
    res_format = []
    for x in res:
        tmp = {
            'user_id': x['id'],
            'email_status': x['properties']['email_send'],
            'email_type': x['properties']['last_behavioral_email_type'],
            'email_round': x['properties']['n1v1_email_round'],
        }
        res_format.append(tmp)

    res_trans = {
        'round_1':{
            'Wait': 0,
            'Ready': 0,
            'Pending': 0,
            'Review Completed': 0,
            'Sent': 0
        },
        'round_2': {
            'Wait': 0,
            'Ready': 0,
            'Pending': 0,
            'Review Completed': 0,
            'Sent': 0
        },
    }

    for x in res_format:
        if x['email_round'] not in ['round_1', 'round_2']:
            continue
        if x['email_status'] not in ['Wait', 'Ready', 'Pending', 'Review Completed', 'Sent']:
            continue

        res_trans[x['email_round']][x['email_status']] += 1

    return res_trans


if __name__ == '__main__':
    res = get_contacts_email_send_status()
    print(res)

