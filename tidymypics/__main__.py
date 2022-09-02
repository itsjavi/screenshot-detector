import sys
import getopt
import os
import pathlib
import tensorflow as tf
from . import core as co

SCRIPT_DIR = os.path.dirname(__file__)


def to_abspath(path):
    return os.path.abspath(os.path.join(SCRIPT_DIR, path))


def print_err(phrase: str) -> None:
    print("ERROR: " + phrase)


def get_validated_args():
    help_text = pathlib.Path(to_abspath('USAGE.txt')).read_text()
    training_mode = False
    by_year = False

    _args = sys.argv
    del _args[0]  # first arg is always current file

    if len(_args) == 0:
        print(help_text)
        sys.exit(0)

    opts, args = getopt.getopt(_args, "ht:y:", ["help", "train", "year"])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_text)
            sys.exit(0)
        elif opt in ("-t", "--train"):
            training_mode = True
        elif opt in ("-y", "--year"):
            by_year = True

    if len(args) != 2:
        print_err("This app needs exactly 2 arguments: SOURCE_PATH and DEST_PATH.")
        sys.exit(1)

    src_dir = os.path.abspath(args[0])
    dest_dir = os.path.abspath(args[1])

    if not os.path.isdir(src_dir) or len(src_dir) == 0:
        # Both modes should have a valid SOURCE_PATH
        print(
            f"SOURCE_PATH ERROR: '{src_dir}' is not a valid existing directory."
        )
        sys.exit(1)

    if training_mode == True and not os.path.isdir(dest_dir) or len(dest_dir) == 0:
        # Training mode should have an existing DEST_PATH
        print(
            f"DEST_PATH ERROR: '{dest_dir}' is not a valid existing directory."
        )
        sys.exit(1)

    if training_mode == False and os.path.isdir(dest_dir):
        # attempting to use an existing dir to output the organized photo library in
        print(
            f"DEST_PATH ERROR: '{dest_dir}' already exists and cannot be used as output directory."
        )
        sys.exit(1)

    return {
        "src_dir": src_dir,
        "dest_dir": dest_dir,
        "training_mode": training_mode,
        "albums_by_year": by_year
    }


def main() -> int:
    # show only tensorflow errors, hide warnings and debug messages
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    tf.get_logger().setLevel('ERROR')

    args = get_validated_args()

    print("TENSORFLOW =", co.versions())
    print("CONFIG =", args)

    if args['training_mode'] == True:
        print("TRAINING A NEW MODEL...")
        (class_names, model_summary, model_history, classif_report, test_pred_df) = co.train_test_model(
            dataset_dir=args['src_dir'],
            test_dir=args['dest_dir'],
            img_size=co.IMG_SIZE,
            batch_size=32,
            validation_split=0.2,
            seed=3224,
            epochs=15
        )

        print("MODEL ACCURACY: ")
        print(classif_report)

        print("TEST RESULTS: ")
        print(test_pred_df.to_string())
    else:
        print("ORGANIZING IMAGES...")
        co.organize_images_dir(args['src_dir'], args['dest_dir'], by_year=args['albums_by_year'])

    return 0


if __name__ == '__main__':
    sys.exit(main())
