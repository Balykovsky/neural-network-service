import os, shutil
from neural_network_service.settings import BASE_DIR


def delete_task_data(task):
    result_dir = os.path.join(BASE_DIR, 'results', task.task_id)
    if os.path.isdir(result_dir):
        shutil.rmtree(result_dir)
        task.delete()