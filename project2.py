# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "numpy>=2.4.4",
#     "scipy>=1.17.1",
# ]
# ///
from scipy.io import wavfile
import numpy as np

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
    samples_per_bit = sample_rate // baud_rate
    print(f"\t{samples_per_bit} samples per bit")
    print(f"\ttotal number of bits in the message:  {data.shape[0] // samples_per_bit}")

def tone_power(samples, N, f, fs):
    """
    Determine the power of the sample data at the given frequency
    :param samples: The data
    :param N: The size of the sample data
    :param f: The frequency to examine
    :param fs: The sample rate of the data
    :return: The power at the given frequency
    """
    I = 0
    Q = 0
    for n in range(N):
        angle = 2 * np.pi * f * n / fs
        I += samples[n] * np.cos(angle)
        Q += samples[n] * np.sin(angle)
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

def wav_to_text(wav_file_name):
    """
    Read wav data as 300 baud receiving data and translate into text
    :param wav_file_name: location of the wav file
    :return: string of ASCII characters
    :raises: ValueError if wav_file_name is stereo
    """
    baud_rate = 300
    sample_rate, data = wavfile.read(wav_file_name)
    if len(data.shape) != 1:
        raise ValueError('wav file must be mono')
    describe_wav_data_details(wav_file_name, data, sample_rate, baud_rate)

    samples_per_bit = sample_rate // baud_rate
    f_zero = 2025
    f_one = 2225
    bits = []
    for i in range(0, data.shape[0] // samples_per_bit):
        bit_data = data[i * samples_per_bit: (i + 1) * samples_per_bit]
        zero = tone_power(bit_data, samples_per_bit, f_zero, sample_rate)
        one = tone_power(bit_data, samples_per_bit, f_one, sample_rate)
        if zero > one:
            bits.append(0)
        else:
            bits.append(1)

    message = ""
    for i in range(0, len(bits) // 10):
        message += chr(data_bits_to_byte(bits[i * 10:(i+1) * 10]))

    return message

if __name__ == '__main__':
    """
    Given received 300 baud modem data encoded in a wav file, decode and print the message
    """
    file_name = 'message.wav'
    text = wav_to_text(file_name)
    with open('message.txt', 'w') as f:
        f.write(text)
    print(f'The message in {file_name} is "{text}"')
