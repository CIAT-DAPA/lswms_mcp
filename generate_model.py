from datamodel_code_generator.inputs import OpenAPI
from datamodel_code_generator.outputs import PydanticV2Output
from pathlib import Path

# Download or reference your API spec
OpenAPI(
    source=Path("apispec_1.json"),
    output=Path("models.py"),
    output_model_type=PydanticV2Output,
).generate()

print("Models generated in models.py")
