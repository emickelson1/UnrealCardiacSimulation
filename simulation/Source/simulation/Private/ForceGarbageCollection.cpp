// Fill out your copyright notice in the Description page of Project Settings.

#include "Engine/StreamableManager.h"
#include "Engine/AssetManager.h"
#include "Engine/Engine.h"
#include "ForceGarbageCollection.h"

void UForceGarbageCollection::ForceGarbageCollection(){
    // // Unload unused assets TArray<FPrimaryAssetId> assetsToUnload
    // if (UAssetManager* assetManager = GEngine->GetEngineSubsystem<UAssetManager>())
    // {
    //     assetManager->UnloadPrimaryAssets(assetsToUnload);
    // }

    CollectGarbage(GARBAGE_COLLECTION_KEEPFLAGS);
    GEngine->ForceGarbageCollection();
}