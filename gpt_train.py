import os
import gc
from pathlib import Path
from trainer import Trainer, TrainerArgs

from TTS.config.shared_configs import BaseDatasetConfig
from TTS.tts.datasets import load_tts_samples
from TTS.tts.layers.xtts.trainer.gpt_trainer import GPTArgs, GPTTrainer, GPTTrainerConfig, XttsAudioConfig
from TTS.utils.manage import ModelManager
import shutil
import math
import csv

def get_epochs_number(train_csv, batch_size, num_epochs=0):
    def calculate_epochs(total_samples, batch_size, target_steps):
        steps_per_epoch = total_samples / batch_size
        num_epochs = math.ceil(target_steps / steps_per_epoch)
        return num_epochs

    def count_samples_in_csv(csv_file_path):
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            sample_count = sum(1 for row in reader)
        return sample_count

    if num_epochs == 0:
        total_samples = count_samples_in_csv(train_csv)
        if total_samples > 1000:
            target_steps = 30000
        elif 600 <= total_samples < 1000:
            target_steps = 20000
        elif 250 <= total_samples < 600:
            target_steps = 15000
        else:
            target_steps = 10000
        num_epochs = calculate_epochs(total_samples, batch_size, target_steps)
    return num_epochs

def train_gpt(config_xtts):
    """
    Huấn luyện GPT với các tham số được định nghĩa trong biến config.
    """

    # Truy cập các tham số từ config
    custom_model = config_xtts.get('custom_model', "")
    version = config_xtts.get('version', "main")
    language = config_xtts.get('language', "vi")
    batch_size = config_xtts.get('batch_size', 2)
    grad_acumm = config_xtts.get('grad_acumm', 1)
    dataset_path = config_xtts.get('dataset_path')
    if dataset_path:
        train_csv = os.path.join(dataset_path, 'train.csv')
        eval_csv = os.path.join(dataset_path, 'eval.csv')
    else:
        print("Hãy thiết lập đường dẫn đến thư mục chứa các file huấn luyện")
        return
    num_epochs = config_xtts.get('epochs', 0)
    if num_epochs == 0:
        num_epochs = get_epochs_number(train_csv, batch_size)
        print(f'num_epochs: {num_epochs}')
    output_path = config_xtts.get('output_path', dataset_path)

    OUT_PATH = os.path.join(output_path, "run", "training")
    # Define the dataset for fine-tuning
    config_dataset = BaseDatasetConfig(
        formatter=config_xtts['formatter'],
        dataset_name=config_xtts['dataset_name'],
        path=dataset_path,
        meta_file_train=train_csv,
        meta_file_val=eval_csv,
        language=language,
    )

    DATASETS_CONFIG_LIST = [config_dataset]

    # Checkpoints file paths
    CHECKPOINTS_OUT_PATH = os.path.join(Path.cwd(), "models", f"{version}")
    os.makedirs(CHECKPOINTS_OUT_PATH, exist_ok=True)

    DVAE_CHECKPOINT_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/review comic/main/dvae.pth"
    MEL_NORM_LINK = "https://coqui.gateway.scarf.sh/hf-coqui/review comic/main/mel_stats.pth"

    DVAE_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(DVAE_CHECKPOINT_LINK))
    MEL_NORM_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(MEL_NORM_LINK))

    custom_model = config_xtts.get("pretrain_model")
    if not custom_model:
        from scripts.modeldownloader import download_model
        download_model(Path(__file__).parent, version)
        custom_model = Path(__file__).parent / f'models/{version}/model.pth'

    if not os.path.isfile(DVAE_CHECKPOINT) or not os.path.isfile(MEL_NORM_FILE):
        print(" > Downloading DVAE files!")
        ModelManager._download_model_files([MEL_NORM_LINK, DVAE_CHECKPOINT_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True)

    TOKENIZER_FILE_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/review comic/{version}/vocab.json"
    XTTS_CHECKPOINT_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/review comic/{version}/model.pth"
    XTTS_CONFIG_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/review comic/{version}/config.json"
    XTTS_SPEAKER_LINK = f"https://coqui.gateway.scarf.sh/hf-coqui/review comic/{version}/speakers_xtts.pth"
    TOKENIZER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(TOKENIZER_FILE_LINK))
    XTTS_CHECKPOINT = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CHECKPOINT_LINK))
    XTTS_CONFIG_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_CONFIG_LINK))
    XTTS_SPEAKER_FILE = os.path.join(CHECKPOINTS_OUT_PATH, os.path.basename(XTTS_SPEAKER_LINK))
    if not os.path.isfile(TOKENIZER_FILE) or not os.path.isfile(XTTS_CHECKPOINT):
        print(f" > Downloading XTTS v{version} files!")
        ModelManager._download_model_files([TOKENIZER_FILE_LINK, XTTS_CHECKPOINT_LINK, XTTS_CONFIG_LINK, XTTS_SPEAKER_LINK], CHECKPOINTS_OUT_PATH, progress_bar=True)

    READY_MODEL_PATH = os.path.join(output_path, "ready")
    if not os.path.exists(READY_MODEL_PATH):
        os.makedirs(READY_MODEL_PATH)

    NEW_TOKENIZER_FILE = os.path.join(READY_MODEL_PATH, "vocab.json")
    NEW_XTTS_CONFIG_FILE = os.path.join(READY_MODEL_PATH, "config.json")
    NEW_XTTS_SPEAKER_FILE = os.path.join(READY_MODEL_PATH, "speakers_xtts.pth")

    shutil.copy(TOKENIZER_FILE, NEW_TOKENIZER_FILE)
    shutil.copy(XTTS_CONFIG_FILE, NEW_XTTS_CONFIG_FILE)
    shutil.copy(XTTS_SPEAKER_FILE, NEW_XTTS_SPEAKER_FILE)

    # Use from ready folder
    TOKENIZER_FILE = NEW_TOKENIZER_FILE
    XTTS_CONFIG_FILE = NEW_XTTS_CONFIG_FILE
    XTTS_SPEAKER_FILE = NEW_XTTS_SPEAKER_FILE

    # Model arguments and configurations
    model_args = GPTArgs(
        max_conditioning_length=132300,
        min_conditioning_length=66150,
        debug_loading_failures=False,
        max_wav_length=255995,
        max_text_length=200,
        mel_norm_file=MEL_NORM_FILE,
        dvae_checkpoint=DVAE_CHECKPOINT,
        xtts_checkpoint=XTTS_CHECKPOINT,
        tokenizer_file=TOKENIZER_FILE,
        gpt_num_audio_tokens=1026,
        gpt_start_audio_token=1024,
        gpt_stop_audio_token=1025,
        gpt_use_masking_gt_prompt_approach=True,
        gpt_use_perceiver_resampler=True,
    )

    # Audio configuration
    audio_config = XttsAudioConfig(sample_rate=config_xtts['audio']['sample_rate'], dvae_sample_rate=config_xtts['audio']['dvae_sample_rate'], output_sample_rate=config_xtts['audio']['output_sample_rate'])

    # Training configuration
    config = GPTTrainerConfig(
        epochs=num_epochs,
        output_path=OUT_PATH,
        model_args=model_args,
        run_name=config_xtts['run_name'],
        project_name=config_xtts['project_name'],
        run_description="GPT XTTS training",
        dashboard_logger=config_xtts['dashboard_logger'],
        logger_uri=config_xtts['logger_uri'],
        audio=audio_config,
        batch_size=batch_size,
        batch_group_size=config_xtts['batch_group_size'],
        eval_batch_size=batch_size,
        num_loader_workers=config_xtts['num_loader_workers'],
        eval_split_max_size=config_xtts['eval_split_max_size'],
        print_step=config_xtts['print_step'],
        plot_step=config_xtts['plot_step'],
        log_model_step=config_xtts['log_model_step'],
        save_step=config_xtts['save_step'],
        save_n_checkpoints=config_xtts['save_n_checkpoints'],
        save_checkpoints=config_xtts['save_checkpoints'],
        save_all_best=config_xtts['save_all_best'],
        languages=config_xtts['languages'],
        precision=config_xtts['precision'],
        mixed_precision=config_xtts['mixed_precision'],
        optimizer=config_xtts['optimizer'],
        optimizer_wd_only_on_weights=True, # for multi-gpu training please make it False
        optimizer_params=config_xtts['optimizer_params'],
        lr=config_xtts['lr'],
        lr_scheduler=config_xtts['lr_scheduler'],
        lr_scheduler_params=config_xtts['lr_scheduler_params'],
        shuffle=config_xtts['shuffle'],
        cudnn_benchmark=config_xtts['cudnn_benchmark'],
        use_grad_scaler=config_xtts['use_grad_scaler'],
        test_sentences=[],
    )

    # Initialize the model
    model = GPTTrainer.init_from_config(config)

    # Load training samples
    train_samples, eval_samples = load_tts_samples(
        DATASETS_CONFIG_LIST,
        eval_split=True,
        eval_split_max_size=config.eval_split_max_size,
        eval_split_size=config.eval_split_size,
    )

    # Train the model
    trainer = Trainer(
        TrainerArgs(
            restore_path=custom_model,
            skip_train_epoch=False,
            start_with_eval=True, # if True it will start with evaluation
            grad_accum_steps=grad_acumm,
        ),
        config,
        output_path=OUT_PATH,
        model=model,
        train_samples=train_samples,
        eval_samples=eval_samples,
    )
    trainer.fit()

    # Get the longest text audio file to use as speaker reference
    samples_len = [len(item["text"].split(" ")) for item in train_samples]
    longest_text_idx = samples_len.index(max(samples_len))
    speaker_ref = train_samples[longest_text_idx]["audio_file"]
    trainer_out_path = trainer.output_path
    # Deallocate VRAM and RAM
    del model, trainer, train_samples, eval_samples
    gc.collect()

    print(f"Training completed and final model saved at {trainer_out_path}")
    return XTTS_SPEAKER_FILE,XTTS_CONFIG_FILE, XTTS_CHECKPOINT, TOKENIZER_FILE, trainer_out_path, speaker_ref
