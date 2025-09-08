import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import os
from dotenv import load_dotenv

from pipeline.transformers import ParseCSVFn, SanitizeAndStructureFn, format_output

load_dotenv()

BUCKET = os.environ.get('BUCKET')

pipe_options_dict = {
    "project": os.environ.get('PROJECT'),
    "region": os.environ.get('REGION'),
    "runner": os.environ.get('RUNNER'),
    "staging_location": f"gs://{BUCKET}/{os.environ.get('STAGING_LOCATION')}",
    "temp_location": f"gs://{BUCKET}/{os.environ.get('TEMP_LOCATION')}",
    "template_location": f"gs://{BUCKET}/{os.environ.get('TEMPLATE_LOCATION')}",
    "job_name": os.environ.get('JOB_NAME'),
    "setup_file": "./setup.py"
}
pipeline_options = PipelineOptions.from_dictionary(pipe_options_dict)

with beam.Pipeline(options=pipeline_options) as pipe:
    pedidos_estruturados = (
        pipe
        | 'ReadFile' >> beam.io.ReadFromText(f'gs://{BUCKET}/{os.environ.get("INPUT")}/vendas_faker.csv')
        | 'ParseCSV' >> beam.ParDo(ParseCSVFn())
        | 'SanitizeAndStructure' >> beam.ParDo(SanitizeAndStructureFn())
    )

    sum_canceled = (
        pedidos_estruturados
        | 'FilterCancelled' >> beam.Filter(lambda record: record.get('status_entrega') == 'cancelado')
        | 'MapCancelled' >> beam.Map(lambda record: (record['categoria'], record['valor_frete']))
        | 'SumCancelled' >> beam.CombinePerKey(sum)
    )

    sum_entregue = (
        pedidos_estruturados
        | 'FilterShipped' >> beam.Filter(lambda record: record.get('status_entrega') == 'entregue')
        | 'MapShipped' >> beam.Map(lambda record: (record['categoria'], record['valor_frete']))
        | 'SumShipped' >> beam.CombinePerKey(sum)
    )

    output_sums = (
        (sum_canceled, sum_entregue)
        | 'FlattenResults' >> beam.Flatten()
        | 'FormatCSV' >> beam.Map(format_output)
        | 'WriteToFile' >> beam.io.WriteToText(
            f'gs://{BUCKET}/{os.environ.get("OUTPUT")}/totals_aggregates',
            file_name_suffix='.csv',
            header='categoria,total_frete'
        )
    )
