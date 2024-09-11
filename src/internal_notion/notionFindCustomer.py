def find_customer(notion_session, customer):
    response = notion_session.blocks.children.list('3f24de6e8b184673816984140674cf04')
    resultArray = response['results']
    for result in resultArray:
        try:
            if result['child_page']['title'] == customer:
                customerID = result['id']
        except:
            continue
    if customerID:
        return customerID
