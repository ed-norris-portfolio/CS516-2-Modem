# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "argparse>=1.4.0",
#     "numpy>=2.4.4",
#     "scipy>=1.17.1",
# ]
# ///
from scipy.io import wavfile
import numpy as np
import argparse

def describe_wav_data_details(wav_file_name, data, sample_rate, baud_rate):
    """
    Print wav file data
    :param wav_file_name: The file name
    :param data: The file data
    :param sample_rate: The sample rate
    :param baud_rate: The known baud rate encoded in the file data
    :return: None
    """
    print(f'\n{wav_file_name}:')
    print(f"\tsample rate: {sample_rate} samples / second")
    print(f"\t{data.shape[0]} samples")
    samples_per_bit = sample_rate // baud_rate
    print(f"\t{samples_per_bit} samples per bit (at {baud_rate} baud)")
    print(f"\t{data.shape[0] // samples_per_bit} bits in the message")
    print(f"\t{data.shape[0] // (samples_per_bit * 10)} ASCII characters in the message\n")

def create_power_matrices(f_zero, f_one, sample_rate, samples_per_bit):
    """
    Pre-compute the arrays necessary to calculate power levels at these frequencies
    :param f_zero:
    :param f_one:
    :param sample_rate:
    :param samples_per_bit:
    :return:
    """
    zero_array = []
    one_array = []
    for i in range(samples_per_bit):
        zero_array.append(2 * np.pi * f_zero * i / sample_rate)
        one_array.append(2 * np.pi * f_one * i / sample_rate)
    zero_array = (np.cos(zero_array), np.sin(zero_array))
    one_array = (np.cos(one_array), np.sin(one_array))
    return zero_array, one_array

def tone_power(samples, arr):
    """
    Determine the power of the sample data at the given frequency
    :param samples: The data
    :param arr: Pre-computed array
    :return: The power at the given frequency
    """
    I = np.dot(samples, arr[0])
    Q = np.dot(samples, arr[1])
    return np.square(I) + np.square(Q)

def data_bits_to_byte(bits):
    """
    Convert 10 bits in 8-N-1 format into a single byte, validating the start and stop bits
    :param bits: the 8-N-1 bits
    :return: the encoded byte as an integer
    :raises: ValueError if the start or stop bits are wrong
    """
    assert(len(bits) == 10)
    if bits[0] != 0:
        raise ValueError("wrong start bit")
    if bits[9] != 1:
        raise ValueError("wrong stop bit")

    byte_val = 0
    twos_position = 1
    for bit in bits[1:9]:
        byte_val += bit * twos_position
        twos_position <<= 1
    return byte_val

def wav_to_text(wav_file_name, min_power):
    """
    Read wav data as 300 baud receiving data and translate into text
    :param wav_file_name: location of the wav file
    :param min_power: minimum power level
    :return: string of ASCII characters
    """
    baud_rate = 300
    sample_rate, raw_data = wavfile.read(wav_file_name)
    if len(raw_data.shape) != 1:
        # grab the left channel
        raw_data = raw_data.reshape(len(raw_data) * len(raw_data[0]))[::2]
    normalized_data = raw_data / np.max(np.abs(raw_data))
    describe_wav_data_details(wav_file_name, normalized_data, sample_rate, baud_rate)

    samples_per_bit = sample_rate // baud_rate
    f_zero = 2025
    f_one = 2225
    bits = []

    zero_array, one_array = create_power_matrices(f_zero, f_one, sample_rate, samples_per_bit)
    for i in range(0, normalized_data.shape[0] // samples_per_bit):
        bit_data = normalized_data[i * samples_per_bit: (i + 1) * samples_per_bit]
        zero = tone_power(bit_data, zero_array)
        one = tone_power(bit_data, one_array)
        if zero > min_power and one > min_power:
            if zero > one:
                bits.append(0)
            else:
                bits.append(1)

    message = ""
    i = 0
    while i < len(bits)-9:
        if bits[i] == 0 and bits[i+9] == 1:
            message += chr(data_bits_to_byte(bits[i:i+10]))
            i += 10
        else:
            i += 1

    return message

if __name__ == '__main__':
    """
    Given received 300 baud modem data encoded in a wav file, decode and print the message
    """
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-f", "--file",
        help="Input wav file.",
        default="samples/message.wav",
    )
    ap.add_argument(
        "-p", "--power",
        help="Minimum power level",
        type=float,
        default=10.0,
    )
    args = ap.parse_args()

    try:
        text = wav_to_text(args.file, args.power)
        with open('message.txt', 'w') as f:
            f.write(text)
        print(f'The message in {args.file} is "{text}"')
    except Exception as e:
        print(e)
