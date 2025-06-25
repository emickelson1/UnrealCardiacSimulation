// Fill out your copyright notice in the Description page of Project Settings.

#include "ConvertToNRRD.h"
#include <fstream>
#include <iostream>

const char *NRRD_HEADER = 
    "NRRD0005\n"
    "type: uint8\n"
    "dimension: 4\n"
    "sizes: %d %d %d %d\n"     // fastest to slowest; Y, X, Z (slices), W (time). Starts from low bottom left corner
    "encoding: raw\n"
    "space: left-posterior-superior\n"
    "endian: little\n"
    "content: 0-255 values representing MRI scan results\n"
    "min: 0\n"
    "max: 255\n"
    "labels: coronal sagittal axial time\n"
    "\n";


bool UConvertToNRRD::MakeNRRD(
    const TArray<uint8>& bytes,
    const FDirectoryPath& saveDirectory,
    const FString& fileName,
    const FString& description,
    const int32 sliceCount, 
    const int32 sliceSize,
    const int32 timeSteps
)
{
    // Make header
    FString nrrdHeaderFString = FString::Printf(TEXT(
        "NRRD0005\n"
        "type: uint8\n"
        "dimension: 4\n"
        "sizes: %d %d %d %d\n"
        "encoding: raw\n"
        // "space: left-posterior-superior\n"
        // "space directions: (1 0 0) (0 1 0) (0 0 1) none\n"
        "content: %s\n"
        "min: 0\n"
        "max: 255\n"
        "labels: \"coronal\" \"sagittal\" \"axial\" \"time\"\n"
        "\n"
    ), sliceSize, sliceSize, sliceCount, timeSteps, *description);
    std::string nrrdHeader = std::string(TCHAR_TO_UTF8(*nrrdHeaderFString));

    // Make filepath
    FString filePath = saveDirectory.Path + "/" + fileName + ".nrrd";
    std::string stdFilePath(TCHAR_TO_UTF8(*filePath));

    // Write data to file
    std::ofstream stream;
    stream.open(stdFilePath, std::ofstream::trunc | std::ofstream::binary);
    if (!stream){
        UE_LOG(LogTemp, Error, TEXT("Failed to open file for writing: %s"), *filePath);
        return false;
    }
    stream.write(nrrdHeader.c_str(), FCStringAnsi::Strlen(nrrdHeader.c_str()));
    stream.write(reinterpret_cast<const char*>(bytes.GetData()), bytes.Num());
    stream.close();

    return true;
}