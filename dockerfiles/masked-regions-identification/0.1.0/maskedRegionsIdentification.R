suppressPackageStartupMessages({
  library(dplyr)
  library(bedtoolsr)
})

main <- function(){
  args <- commandArgs(trailingOnly = TRUE)
  path2GeneBuildMask <- args[1]
  path2maskFile <- args[2]
  if( length(args) == 3){
    pathControlFiles <- args[3]
    msg <- 'Mask file will be generated from control peaks'
  }else{
    pathControlFiles <- NULL
    msg <- 'Mask file will be generated from DUST/TRF regions'
  }
  
  print(msg)
  
  mergingDistance <- 20
  minEpis <- 5
  minRegionLength <- 50
  overlapPerc <- 50/100

  # Loading gene-build repeats
  geneBuildMask <- read.delim(path2GeneBuildMask,header = FALSE)
  
  # Extracting only DUST/TRF regions and merging the overlapping ones
  geneBuildMask <- geneBuildMask[geneBuildMask[,4] %in% c('dust', 'trf'), 1:3]
  geneBuildMask <- bt.merge(bt.sort(geneBuildMask))
  
  names(geneBuildMask) <- c('chr', 'start', 'end')
  
  if( !is.null(pathControlFiles)){
    controlFiles <- list.files(path = pathControlFiles)
    controlFiles <- controlFiles[grep('.bed', controlFiles)]
    if(length(controlFiles) == 0){
      stop("Error: Not control peak files are available in the provided folder")
    }
    # Loading peaks identified at the epigenome level from control experiments 
    controlFiles <- list.files(path = pathControlFiles)
    controlPeaks <- list()
    for(i in 1:length(controlFiles)){
      controlPeaks[[controlFiles[i]]] <- read.delim(paste(pathControlFiles, 
                                                          controlFiles[i],
                                                          sep ='/'),
                                                    header = F)
    }
    
    # Getting set of union peaks
    unionPeaks <- NULL
    for(i in 1:length(controlPeaks)){
      controlPeaks[[i]] <- bt.merge(controlPeaks[[i]], d = mergingDistance)
      unionPeaks <- rbind(unionPeaks, controlPeaks[[i]])
      unionPeaks <- bt.merge(bt.sort(unionPeaks), d = mergingDistance)
    }
    
    names(unionPeaks) <- c('chr', 'start', 'end')
    
    # Identification of peaks across epigenomes
    unionPeaksInEpis <- NULL
    for(i in 1:length(controlPeaks)){
      unionPeaksInEpis <- rbind(unionPeaksInEpis, 
                                cbind(bt.intersect(unionPeaks, controlPeaks[[i]], 
                                                   u = TRUE, wa = TRUE),
                                      bedFile=names(controlPeaks)[i]))
    }
    names(unionPeaksInEpis)[1:3] <- c('chr', 'start', 'end')
    unionPeaksInEpis <- cbind(unionPeaksInEpis, 
                              loc=paste(unionPeaksInEpis$chr, 
                                        paste(unionPeaksInEpis$start, 
                                              unionPeaksInEpis$end, 
                                              sep = '-'), 
                                        sep = ':'))
    unionPeaksInEpis %>%
      group_by(loc) %>%
      summarise(n=n()) -> unionPeaksInEpisCount
    
    # Counting peaks across epigenomes
    unionPeaksInEpisCount$chr <- do.call(rbind,
                                         strsplit(unionPeaksInEpisCount$loc,
                                                  split=":"))[,1]
    unionPeaksInEpisCount$start <- do.call(rbind, strsplit(
      do.call(rbind,
              strsplit(unionPeaksInEpisCount$loc, 
                       split=":"))[,2], 
      split = '-'))[,1]
    
    unionPeaksInEpisCount$end <- do.call(rbind, strsplit(
      do.call(rbind,
              strsplit(unionPeaksInEpisCount$loc,
                       split=":"))[,2], 
      split = '-'))[,2]
    rownames(unionPeaks) <- paste(unionPeaks$chr,
                                  paste(unionPeaks$start, 
                                        unionPeaks$end, 
                                        sep = '-'), 
                                  sep = ':')
    
    # Identification of regions of interests
    cond <- unionPeaksInEpisCount$n >= minEpis
    unionPeaksInEpis <- unionPeaks[unionPeaksInEpisCount$loc[cond],]
    unionPeaksnotInEpis <- unionPeaks[unionPeaksInEpisCount$loc[!cond],]
    
    # Peaks satisfying the condition that overlap any DUST/TRF region or
    # peaks that do not satisfy the condition but overlap with any DUST/TRF 
    # region of at least 50bp will be kept
    
    e111Mask <- rbind(bt.intersect(unionPeaksInEpis, geneBuildMask,
                                   wa = TRUE, 
                                   wb = TRUE),
                      bt.intersect(unionPeaksnotInEpis, 
                                   geneBuildMask[(geneBuildMask$end - 
                                                    geneBuildMask$start) >= 
                                                   minRegionLength, ],
                                   wa = TRUE, wb = TRUE, f = overlapPerc, 
                                   F = overlapPerc, e = TRUE))
    
    names(e111Mask) <- c('chr', 'start', 'end', 'chrM', 'startM', 'endM')                                   
    
    # Peaks will be extended to the minimum start and maximum end between union 
    # peaks and the overlapped DUST/TRF regions
    e111Mask[,'start'] <- apply(e111Mask[,c('start', 'startM')],
                                1, min)
    e111Mask[,'end'] <- apply(e111Mask[,c('end', 'endM')],
                              1, max)
    e111Mask <- bt.merge(bt.sort(e111Mask[,c('chr', 'start', 'end')]), 
                         d = mergingDistance)
    
  }else{
    
    # Merging DUST/TRF regions nearby up to mergingDistance bp and keeping 
    # regions longer than minRegionLength
    e111Mask <- bt.merge(bt.sort(geneBuildMask), d = mergingDistance)
    e111Mask <- e111Mask[e111Mask[,3] - e111Mask[,2] > minRegionLength, ]
  }
    
  # Exporting masked regions
  write.table(x = e111Mask, file = path2maskFile, quote = F, row.names = F,
              col.names = F, sep = '\t')
}

main()
