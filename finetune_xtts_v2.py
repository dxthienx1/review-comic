from gpt_train import train_gpt
from pathlib import Path
from common_function import *
config_xtts = get_json_data(config_xtts_path)
output_path = os.path.join(current_dir, config_xtts.get('output_path'))
dataset_path = os.path.join(current_dir, config_xtts.get('dataset_path'))
config_xtts['dataset_path'] = dataset_path
custom_model_folder = os.path.join(current_dir, config_xtts.get('custom_model'))
custom_model = get_custom_model(custom_model_folder)
config_xtts['custom_model'] = custom_model

def clear_gpu_cache():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def train_model(config_xtts):
    clear_gpu_cache()
    run_dir = Path(output_path) / 'run'
    if run_dir.exists():
        shutil.rmtree(run_dir)

    try:
        speaker_xtts_path, config_path, original_xtts_checkpoint, vocab_file, exp_path, speaker_wav = train_gpt(config_xtts)
    except Exception as e:
        traceback.print_exc()
        raise e

    ready_dir = Path(output_path) / 'ready'
    ft_xtts_checkpoint = os.path.join(exp_path, "best_model.pth")
    shutil.copy(ft_xtts_checkpoint, ready_dir / "unoptimize_model.pth")
    ft_xtts_checkpoint = os.path.join(ready_dir, "unoptimize_model.pth")
    speaker_reference_path = Path(speaker_wav)
    speaker_reference_new_path = ready_dir / "reference.wav"
    shutil.copy(speaker_reference_path, speaker_reference_new_path)
    print("Model training done!")
    return config_path, vocab_file, ft_xtts_checkpoint, speaker_xtts_path, speaker_reference_new_path

def optimize_model(clear_train_data=None):
    out_path = Path(output_path)
    ready_dir = out_path / "ready"
    run_dir = out_path / "run"
    dataset_dir = out_path / "dataset"
    if clear_train_data in {"run", "all"} and run_dir.exists():
        shutil.rmtree(run_dir)
    if clear_train_data in {"dataset", "all"} and dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    model_path = ready_dir / "unoptimize_model.pth"
    if not model_path.is_file():
        raise Exception("Unoptimized model not found in ready folder")
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
    del checkpoint["optimizer"]
    for key in list(checkpoint["model"].keys()):
        if "dvae" in key:
            del checkpoint["model"][key]
    os.remove(model_path)
    optimized_model_file_name = "model.pth"
    optimized_model = ready_dir / optimized_model_file_name
    torch.save(checkpoint, optimized_model)
    ft_xtts_checkpoint = str(optimized_model)
    clear_gpu_cache()
    return ft_xtts_checkpoint

def load_params():
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise Exception(f"Output folder does not exist at {dataset_path}")
    eval_train = dataset_path / "train.csv"
    eval_csv = dataset_path / "eval.csv"

    current_language = config_xtts.get('language', 'vi')
    clear_gpu_cache()
    return eval_train, eval_csv, current_language

def read_dataset_queue(json_file):
    with open(json_file, 'r') as file:
        datasets = json.load(file)
    active_datasets = [d['path'] for d in datasets if d.get('activate', False)]
    return active_datasets

def run_training_pipeline():
    try:
        train_model(config_xtts)
        optimize_model()
    except:
        getlog()

# Thay thế terminal input bằng cách gọi trực tiếp hàm
if __name__ == "__main__":
    run_training_pipeline()
