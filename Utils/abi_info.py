from Crypto.Hash import keccak


def obtain_hash_event(event):
    k = keccak.new(digest_bits=256)
    k.update(bytes(event, encoding='utf-8'))
    return '0x'+k.hexdigest()

def obtain_events_from_abi(abi):
    events = []
    for function in abi:
        if function['type'] == 'event':
            event = function['name'] + '('
            contador = 0
            for element in function['inputs']:
                if contador == 0:
                    event += element['type']

                else:
                    event += ','+element['type']

                contador+=1

            event  += ')'
            events.append(event)

    return events