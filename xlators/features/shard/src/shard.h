/*
  Copyright (c) 2015 Red Hat, Inc. <http://www.redhat.com>
  This file is part of GlusterFS.

  This file is licensed to you under your choice of the GNU Lesser
  General Public License, version 3 or any later version (LGPLv3 or
  later), or the GNU General Public License, version 2 (GPLv2), in all
  cases as published by the Free Software Foundation.
*/


#ifndef __SHARD_H__
#define __SHARD_H__

#ifndef _CONFIG_H
#define _CONFIG_H
#include "config.h"
#endif

#include "xlator.h"
#include "compat-errno.h"

#define GF_SHARD_DIR ".shard"
#define SHARD_MIN_BLOCK_SIZE  (4 * GF_UNIT_MB)
#define SHARD_MAX_BLOCK_SIZE  (4 * GF_UNIT_TB)
#define GF_XATTR_SHARD_BLOCK_SIZE "trusted.glusterfs.shard.block-size"
#define SHARD_ROOT_GFID "be318638-e8a0-4c6d-977d-7a937aa84806"
#define SHARD_INODE_LRU_LIMIT 4096

#define get_lowest_block(off, shard_size) (off / shard_size)
#define get_highest_block(off, len, shard_size) ((off+len-1) / shard_size)

#define SHARD_ENTRY_FOP_CHECK(loc, op_errno, label) do {               \
        if ((loc->name && !strcmp (GF_SHARD_DIR, loc->name)) &&        \
            (((loc->parent) &&                                          \
            __is_root_gfid (loc->parent->gfid)) ||                     \
            __is_root_gfid (loc->pargfid))) {                           \
                    op_errno = EPERM;                                  \
                    goto label;                                        \
        }                                                              \
                                                                       \
        if ((loc->parent &&                                            \
            __is_shard_dir (loc->parent->gfid)) ||                     \
            __is_shard_dir (loc->pargfid)) {                           \
                    op_errno = EPERM;                                  \
                    goto label;                                        \
        }                                                              \
} while (0)

#define SHARD_INODE_OP_CHECK(gfid, err, label) do {                    \
        if (__is_shard_dir(gfid)) {                                    \
                err = EPERM;                                           \
                goto label;                                            \
        }                                                              \
} while (0)

#define SHARD_STACK_UNWIND(fop, frame, params ...) do {       \
        shard_local_t *__local = NULL;                         \
        if (frame) {                                           \
                __local = frame->local;                        \
                frame->local = NULL;                           \
        }                                                      \
        STACK_UNWIND_STRICT (fop, frame, params);              \
        if (__local) {                                         \
                shard_local_wipe (__local);                    \
                mem_put (__local);                             \
        }                                                      \
} while (0)                                                    \

typedef struct shard_priv {
        uint64_t block_size;
        uuid_t dot_shard_gfid;
        inode_t *dot_shard_inode;
} shard_priv_t;

typedef struct {
        loc_t *loc;
        short type;
        char *domain;
} shard_lock_t;

typedef struct shard_local {
        int op_ret;
        int op_errno;
        int first_block;
        int last_block;
        int num_blocks;
        int call_count;
        int eexist_count;
        int xflag;
        int count;
        uint32_t flags;
        uint64_t block_size;
        off_t offset;
        size_t total_size;
        size_t written_size;
        loc_t loc;
        loc_t dot_shard_loc;
        fd_t *fd;
        dict_t *xattr_req;
        inode_t **inode_list;
        struct iovec *vector;
        struct iobref *iobref;
        struct {
                int lock_count;
                fop_inodelk_cbk_t inodelk_cbk;
                shard_lock_t *shard_lock;
        } lock;
} shard_local_t;

typedef struct shard_inode_ctx {
        uint32_t rdev;
        uint64_t block_size; /* The block size with which this inode is
                                sharded */
        mode_t mode;
} shard_inode_ctx_t;

#endif /* __SHARD_H__ */
