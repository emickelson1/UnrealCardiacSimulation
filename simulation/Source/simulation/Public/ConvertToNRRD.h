// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "ConvertToNRRD.generated.h"

/**
 * 
 */
UCLASS()
class SIMULATION_API UConvertToNRRD : public UGameInstanceSubsystem
{
	GENERATED_BODY()
	
public:
	UFUNCTION(BlueprintCallable, Category = "Capture")
	bool MakeNRRD(
		const TArray<uint8>& bytes,
		const FDirectoryPath& saveDirectory,
		const FString& fileName,
		const FString& description,
		const int32 sliceCount, 
		const int32 sliceSize,
		const int32 timeSteps
	);
};