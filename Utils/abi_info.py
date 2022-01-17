from Crypto.Hash import keccak


def obtain_hash_event(event: str) -> str:
    k = keccak.new(digest_bits=256)
    k.update(bytes(event, encoding='utf-8'))
    return '0x'+k.hexdigest()


def obtain_events_from_abi(abi: dict) -> list:
    events = []
    for function in abi:
        if function['type'] == 'event':
            event = function['name'] + '('
            for cont, element in enumerate(function['inputs']):
                if cont == 0:
                    event += element['type']

                else:
                    event += ','+element['type']

                cont += 1

            event  += ')'
            events.append(event)

    return events
