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
	bool MakeNRRDs(
		const TArray<uint8>& volumes,
		const TArray<uint8>& segmentations,
		const FString& dataset,
		const FString& name,
		const FString& description,
		const int32 timeSteps,
		const int32 sliceX,
		const int32 sliceY,
		const int32 sliceZ,
		const float spacingX,
		const float spacingY,
		const float spacingZ
	);

private:
	bool MakeVolume(
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
	);
	bool MakeSegmentation(
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
	);
};