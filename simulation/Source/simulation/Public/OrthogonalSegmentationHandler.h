// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Camera/CameraComponent.h"
#include "OrthogonalSegmentationHandler.generated.h"

/**
 * 
 */
UCLASS()
class SIMULATION_API UOrthogonalSegmentationHandler : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Capture")
	void CaptureScreenshot(const UCameraComponent* Camera, const FString& Directory);

	UFUNCTION(BlueprintCallable, Category = "Capture")
	void CaptureSegmentation(const UCameraComponent* Camera, const FString& Directory);
};
