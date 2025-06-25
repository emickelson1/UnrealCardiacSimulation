// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MRITraceHandler.generated.h"

/**
 * 
 */
UCLASS()
class SIMULATION_API UMRITraceHandler : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Capture")
	void MRIScan(
		const int32 sliceCount, 
		const int32 sliceSize, 
		const FVector& minBounds, 
		const FVector& maxBounds, 
		TArray<uint8>& slices, 
		TArray<uint8>& segmentations
	);
};
