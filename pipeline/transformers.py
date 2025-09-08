import datetime
import csv
from io import StringIO
import apache_beam as beam

class ParseCSVFn(beam.DoFn):
    def process(self, line):
        try:
            if not line.strip():
                return

            reader = csv.reader(StringIO(line))
            values = next(reader)

            if values[0].strip().upper() == 'ID_PEDIDO':
                return

            if len(values) >= 9:
                record = {
                    'id_pedido': values[0].strip(),
                    'data_pedido': values[1].strip(),
                    'id_cliente': values[2].strip(),
                    'nome_cliente': values[3].strip(),
                    'itens_pedido': values[4].strip(),
                    'categoria': values[5].strip(),
                    'status_entrega': values[6].strip(),
                    'cidade_entrega': values[7].strip(),
                    'valor_frete': values[8].strip()
                }
                yield record
        except Exception:
            pass

class SanitizeAndStructureFn(beam.DoFn):
    """Now processes dictionaries instead of beam.Row objects"""
    def process(self, record_dict):
        try:
            sanitized_record = {}
            for key, value in record_dict.items():
                new_key = key.lower()
                if isinstance(value, str):
                    new_value = value.strip().lower()
                else:
                    new_value = value
                if new_key == 'data_pedido' and new_value:
                    sanitized_record[new_key] = datetime.datetime.strptime(new_value, '%Y-%m-%d').date()
                elif new_key == 'valor_frete' and new_value:
                    sanitized_record[new_key] = float(new_value)
                else:
                    sanitized_record[new_key] = new_value
            yield sanitized_record
        except (ValueError, TypeError, AttributeError):
            pass

def format_output(element):
    return f"{element[0]},{element[1]}"
