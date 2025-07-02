// Fill out your copyright notice in the Description page of Project Settings.

#include "ConvertToNRRD.h"
#include <fstream>
#include <iostream>

bool UConvertToNRRD::MakeNRRDs(
    const TArray<uint8>& volumes,
    const TArray<uint8>& segmentations,
    const FDirectoryPath& saveDirectory,
    const FString& fileName,
    const FString& description,
    const int32 timeSteps,
    const int32 countX,
    const int32 countY,
    const int32 countZ,
    const float spacingX,
    const float spacingY,
    const float spacingZ
)
{
    return (
        MakeVolume(volumes, saveDirectory, fileName, description, timeSteps, countX, countY, countZ, spacingX, spacingY, spacingZ) 
        &&
        MakeSegmentation(segmentations, saveDirectory, fileName, description, timeSteps, countX, countY, countZ, spacingX, spacingY, spacingZ)
    );
}

bool UConvertToNRRD::MakeVolume(
    const TArray<uint8>& volumes,
    const FDirectoryPath& saveDirectory,
    const FString& fileName,
    const FString& description,
    const int32 timeSteps,
    const int32 countX,
    const int32 countY,
    const int32 countZ,
    const float spacingX,
    const float spacingY,
    const float spacingZ
)
{
    // Make header
    FString nrrdHeaderFString = FString::Printf(TEXT(
        "NRRD0005\n"
        "type: uint8\n"
        "dimension: 4\n"
        "sizes: %d %d %d %d\n"
        "encoding: raw\n"
        "space: right-anterior-superior\n"                          // X increases to the right, Y increases forwards, Z increases upwards
        "space origin: (0.0, 0.0, 0.0)\n"
        "space directions: (%f,0,0) (0,-%f,0) (0,0,%f) none\n"
        "content: %s\n"
        "endian: little\n"
        "min: 0\n"
        "max: 255\n"
        "labels: \"sagittal\" \"coronal\" \"axial\" \"time\"\n"
        "kinds: domain domain domain list\n"
        "\n"
    ), countX, countY, countZ, timeSteps, spacingX*10.0f, spacingY*10.0f, spacingZ*10.0f, *description);    // multiply spacings to convert cm to mm
    std::string nrrdHeader = std::string(TCHAR_TO_UTF8(*nrrdHeaderFString));

    // Make filepath
    FString filePath = saveDirectory.Path + "/" + fileName + "_vol.nrrd";
    std::string stdFilePath(TCHAR_TO_UTF8(*filePath));

    // Write data to file
    std::ofstream stream;
    stream.open(stdFilePath, std::ofstream::trunc | std::ofstream::binary);
    if (!stream){
        UE_LOG(LogTemp, Error, TEXT("Failed to open file for writing: %s"), *filePath);
        return false;
    }
    stream.write(nrrdHeader.c_str(), FCStringAnsi::Strlen(nrrdHeader.c_str()));
    stream.write(reinterpret_cast<const char*>(volumes.GetData()), volumes.Num());
    stream.close();

    return true;
}

bool UConvertToNRRD::MakeSegmentation(
    const TArray<uint8>& segmentations,
    const FDirectoryPath& saveDirectory,
    const FString& fileName,
    const FString& description,
    const int32 timeSteps,
    const int32 countX,
    const int32 countY,
    const int32 countZ,
    const float spacingX,
    const float spacingY,
    const float spacingZ
)
{
    // Make header
    FString nrrdHeaderFString = FString::Printf(TEXT(
        "NRRD0005\n"
        "type: uint8\n"
        "dimension: 4\n"
        "sizes: %d %d %d %d\n"
        "encoding: raw\n"
        "space: right-anterior-superior\n"                          // X increases to the right, Y increases forwards, Z increases upwards
        "space origin: (0.0, 0.0, 0.0)\n"
        "space directions: (%f,0,0) (0,-%f,0) (0,0,%f) none\n"
        "content: %s\n"
        "endian: little\n"
        "min: 0\n"
        "max: 255\n"
        "labels: \"sagittal\" \"coronal\" \"axial\" \"time\"\n"
        "kinds: domain domain domain list\n"
        "\n"
    ), countX, countY, countZ, timeSteps, spacingX*10.0f, spacingY*10.0f, spacingZ*10.0f, *description);    // multiply spacings to convert cm to mm
    std::string nrrdHeader = std::string(TCHAR_TO_UTF8(*nrrdHeaderFString));

    // Make filepath
    FString filePath = saveDirectory.Path + "/" + fileName + "_seg.nrrd";
    std::string stdFilePath(TCHAR_TO_UTF8(*filePath));

    // Write data to file
    std::ofstream stream;
    stream.open(stdFilePath, std::ofstream::trunc | std::ofstream::binary);
    if (!stream){
        UE_LOG(LogTemp, Error, TEXT("Failed to open file for writing: %s"), *filePath);
        return false;
    }
    stream.write(nrrdHeader.c_str(), FCStringAnsi::Strlen(nrrdHeader.c_str()));
    stream.write(reinterpret_cast<const char*>(segmentations.GetData()), segmentations.Num());
    stream.close();

    return true;
}