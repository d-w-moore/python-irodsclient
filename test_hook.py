import json
import sys

def run (CI):

    final_config = CI.store_config(
        {
            "yaml_substitutions": {
                "db": "postgres",
                "db_port": "5432",
                "return_code": "0",
                "os_image":"hello fm internet"
            },

            "container_environments": {

                "client-runner" : {
                    "PY_VERSION": "3",
                    "IRODS_HOST": "irods-provider" 
                }

            }

        }
    )

    print ('----------\nconfig after CI modify pass\n----------',file=sys.stderr)
    print(json.dumps(final_config,indent=4),file=sys.stderr)

    return CI.run_and_wait_on_client_exit ()
