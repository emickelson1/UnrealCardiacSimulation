// Fill out your copyright notice in the Description page of Project Settings.

#include "ConvertToNRRD.h"
#include <fstream>
#include <iostream>
#include <filesystem>

bool UConvertToNRRD::MakeNRRDs(
    const TArray<uint8>& volumes,
    const TArray<uint8>& segmentations,
    const FString& dataset,
    const FString& name,
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
        MakeVolume(volumes, dataset, name, description, timeSteps, countX, countY, countZ, spacingX, spacingY, spacingZ) 
        && MakeSegmentation(segmentations, dataset, name, description, timeSteps, countX, countY, countZ, spacingX, spacingY, spacingZ)
    );
}

bool UConvertToNRRD::MakeVolume(
    const TArray<uint8>& volumes,
    const FString& dataset,
    const FString& name,
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
    FString rootPath = UTF8_TO_TCHAR(std::filesystem::path(TCHAR_TO_UTF8(*FPaths::GetProjectFilePath())).parent_path().parent_path().string().c_str());
    FString filePath = FString::Printf(TEXT("%s/data/unprocessed/%s/%s_vol.nrrd"), *rootPath, *dataset, *name);
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
    const FString& dataset,
    const FString& name,
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
        "space: right-anterior-superior\n"
        "space origin: (0.0, 0.0, 0.0)\n"
        "space directions: (%f,0,0) (0,-%f,0) (0,0,%f) none\n"
        "content: %s\n"
        "endian: little\n"
        "min: 0\n"
        "max: 255\n"
        "labels: \"sagittal\" \"coronal\" \"axial\" \"time\"\n"
        "kinds: domain domain domain list\n"
        // "Segment0_ID:=Left_Atrium\n"
        // "Segment0_Name:=Left_Atrium\n"
        // "Segment0_Color:=1.0 0.8 0.0\n"
        // "Segment0_LabelValue:=1\n"
        // "Segment0_Extent:=0 399 0 399 0 399\n"
        // "Segment1_ID:=Left_Ventricle\n"
        // "Segment1_Name:=Left_Ventricle\n"
        // "Segment1_Color:=0.0 1.0 1.0\n"
        // "Segment1_LabelValue:=2\n"
        // "Segment1_Extent:=0 399 0 399 0 399\n"
        // "Segment2_ID:=Myocardium\n"
        // "Segment2_Name:=Myocardium\n"
        // "Segment2_Color:=1.0 1.0 0.4\n"
        // "Segment2_LabelValue:=3\n"
        // "Segment2_Extent:=0 399 0 399 0 399\n"
        // "Segment3_ID:=Pulmonary_Artery\n"
        // "Segment3_Name:=Pulmonary_Artery\n"
        // "Segment3_Color:=0.0 1.0 0.0\n"
        // "Segment3_LabelValue:=4\n"
        // "Segment3_Extent:=0 399 0 399 0 399\n"
        // "Segment4_ID:=Right_Atrium\n"
        // "Segment4_Name:=Right_Atrium\n"
        // "Segment4_Color:=1.0 0.0 1.0\n"
        // "Segment4_LabelValue:=5\n"
        // "Segment4_Extent:=0 399 0 399 0 399\n"
        // "Segment5_ID:=Right_Ventricle\n"
        // "Segment5_Name:=Right_Ventricle\n"
        // "Segment5_Color:=0.8 1.0 0.2\n"
        // "Segment5_LabelValue:=6\n"
        // "Segment5_Extent:=0 399 0 399 0 399\n"
        // "Segment6_ID:=Superior_Vena_Cava\n"
        // "Segment6_Name:=Superior_Vena_Cava\n"
        // "Segment6_Color:=0.6 0.6 1.0\n"
        // "Segment6_LabelValue:=7\n"
        // "Segment6_Extent:=0 399 0 399 0 399\n"
        // "Segment7_ID:=Aorta\n"
        // "Segment7_Name:=Aorta\n"
        // "Segment7_Color:=1.0 0.0 0.0\n"
        // "Segment7_LabelValue:=8\n"
        // "Segment7_Extent:=0 399 0 399 0 399\n"
        "\n"
    ), countX, countY, countZ, timeSteps, spacingX*10.0f, spacingY*10.0f, spacingZ*10.0f, *description);
    std::string nrrdHeader = std::string(TCHAR_TO_UTF8(*nrrdHeaderFString));

    // Make filepath
    FString rootPath = UTF8_TO_TCHAR(std::filesystem::path(TCHAR_TO_UTF8(*FPaths::GetProjectFilePath())).parent_path().parent_path().string().c_str());
    FString filePath = FString::Printf(TEXT("%s/data/unprocessed/%s/%s_seg.nrrd"), *rootPath, *dataset, *name);
    std::string stdFilePath(TCHAR_TO_UTF8(*filePath));

    UE_LOG(LogTemp, Warning, TEXT("Output Path: %s"), *filePath);

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